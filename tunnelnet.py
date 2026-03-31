import platform 
import requests
import shlex
import subprocess
import threading
import queue
import warnings
import webbrowser
import sys
from urllib.request import urlopen
from pathlib import Path
from tkinter import *
from tkinter import ttk
import tkinter as tk
import pexpect

userdir = Path(__file__).resolve()

system = platform.system()#OS CHECK STARTS HERE, should return "Windows", "Linux", or "Darwin" for MacOS.
#see official python documentation if confused.
#Nathan keep your code for the installscript inside an if statement checking variable system for OS thanks
CLIENTSECRET = ""
CLIENTID = ""
APIKEY = ""
TAILNET = ""
AUTH = ""
STDOUT = ""
SUDO = ""
USERSAVEDIR = str(userdir.parent)+"/Assets/usersave.txt"
#tunnelnet should only save the clientID. APIKEY cannot be saved and 
#must be requested at user login.
#physical control of local API can be done using cli, my idea is to run
#a daemon thread to do all the terminal stuff using schlex.
inject = pexpect.spawn("/bin/bash", encoding="utf-8")
inject.logfile = sys.stdout
def login(): #login command.
    global APIKEY,CLIENTID,CLIENTSECRET
    CLIENTID = loginentry.get()
    CLIENTSECRET = passentry.get()
    if CLIENTID == "" or CLIENTSECRET == "":
        print("Error: One or more authentication elements are missing!")
    elif CLIENTSECRET == "testing":
        print("login bypassed")
        root.withdraw()
        main.deiconify()
    else:
        status = requesttoken(CLIENTID, CLIENTSECRET)
        print(status)
        status2 = authkey(APIKEY)
        if status == 200 and status2 == 200:
            try:
                with open(USERSAVEDIR, "w") as dingus2:
                    dingus2.write(CLIENTID)
                    print("saved id")
            except Exception as err:
                print(err)
            print("login successful")
            root.withdraw()
            main.deiconify()
        logassemble = f"sudo tailscale up --auth-key={AUTH}"
        cmd_queue.put(logassemble)


def join(): #for the join tab of the initialize window.
    global AUTH
    AUTH = joinentry.get()
    cmd_queue.put(f"tailscale up --auth-key={AUTH}")

def sudofetch(): #determine if sudo works and show next screen if successful.
    global SUDO
    SUDO = authentry.get()
    if SUDO == "":
        print("Error: Nothing in authentication!")
    else:
        cmd_queue.put("echo success!")
        cmd_queue.join()
        if not sudo_ready():
            print("sudo not authenticated, verify contents...")
        else:
            #authentry.delete(0,END)
            authlevel.withdraw()
            root.deiconify()

def bash_worker():
    global STDOUT, SUDO, inject
        
    while True:
        cmd = cmd_queue.get()
        if cmd is None:
            break
        try:
            if sudo_ready() == False:
                try:
                    print("SUDO not detected! Injecting...")
                    inject.sendline("sudo -s")
                    inject.expect(r"[Pp]assword")
                    inject.sendline(SUDO)
                    inject.expect(r"# ", timeout=3)

                except Exception as E:
                    print("sudError: ", E)
            
            #if not cmd.startswith("sudo"):
                #args = shlex.split("sudo "+cmd)
            #else:i 
            '''
            args = shlex.split(cmd)
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode == 0:
                STDOUT = result.stdout
            else:
                print("EXIT:", result.returncode)
                STDOUT = result.stdout
                print("ERR:", result.stderr)
            '''
            #god i want to throw my laptop at a brick wall
            inject.sendline(f"sudo {cmd}")
            inject.expect(r"# ", timeout=2)
            STDOUT = inject.before.split("\r\n", 1)[-1] 


        except Exception as e:
            print("Worker error:", e)
        cmd_queue.task_done()

def sudo_ready(): #checks if sudo is running, returns true or false.
    inject.sendline("sudo -n true && echo READY || echo NEEDPASS")
    i = inject.expect(r"# ",timeout=1)
    output = inject.before.strip()
    if "READY" in output:
        return True
    else:
        return False


def requesttoken(cid, cs):
    global APIKEY,CLIENTID,CLIENTSECRET
    token_url = "https://api.tailscale.com/api/v2/oauth/token"
    response = requests.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=(cid, cs),
    )
    APIKEY = response.json()["access_token"]
    print("key requested: "+APIKEY)
    return response.status_code


def listdevices(apikey, tailnet = "-"):
    token_url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
    response = requests.get(
        token_url,
        headers= {'Authorization':f"Bearer {apikey}"}
    )
    print(response)
    print(response.json())

def authkey(apikey, tailnet = "-"):
    global AUTH
    token_url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/keys"
    response = requests.post(
        token_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer "+apikey
        },
        json={
            "description": "hi there",
            "capabilities": {"devices":{"create":{
                "reusable": False,
                "ephemeral": False,
                "preauthorized": True,
                "tags": ["tag:client"]
            }}},
            "expirySeconds": 86400
        }
    )
    print(response)
    AUTH = (response.json())["key"]
    print("auth: "+AUTH)
    return response.status_code


def getkeystatus(apikey):
    pass

#BASH THREAD STARTER
if system == "Linux":
    cmd_queue = queue.Queue()
    thread = threading.Thread(target=bash_worker, daemon=True)
    thread.start()
else:
    warnings.warn("bash worker thread skipped, login will not work! (use \"testing\" in password to bypass)")

#ROOT CONFIGS
root = Tk()
root.geometry("300x150+200+200")
root.title("tunnelNET: Login")
root.resizable(False,False)
for acol in range(3):
    root.columnconfigure(acol, weight=1)
for brow in range(8):
    root.rowconfigure(brow, weight=1)

#MAINWINDOW CONFIGS
main = Toplevel(root)
main.title("tunnelNET")
main.geometry("600x400+200+200")
main.configure(bg="lightgray")
### We can add more row/columns later
main.columnconfigure(1, weight=3) # for mainchat
main.columnconfigure(0, weight=1) # for profile
main.rowconfigure(1, weight=1) # for chat
main.rowconfigure(0, weight=0) # for computer background image

# Colors (Can be changed in the future; just here for placeholder)
BANNERBG = "#131415"
PROFILEBG = "#1B1C1E"
CHATBG = "#2C2E31"
TEXTBG = "#32363B"
SELECTBG = "#6C727C"

# Commands
def sendMessage():
    message = textbox.get().strip()
    if message == "": # checks message content, then stops empty spaces from being sent
        textbox.delete(0, tk.END) # deletes entry text after enter
    else:
        current_tab = chattab.nametowidget(chattab.select())
        entrytextlabel = tk.Label(current_tab, text=message, anchor="w")
        entrytextlabel.grid(column=0, sticky='w')
        textbox.delete(0, tk.END)

# Image loading
bgimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/main/Assets/computerBackground.png'
logoimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/main/Assets/tunnel.png'
try:
    with urlopen(bgimglink) as img1:
        bgimgraw = img1.read()
    with urlopen(logoimglink) as img2:
        logoimgraw = img2.read()
except Exception as linkerror: 
    print("Fetch logo failed", str(linkerror))

# Images variables
bgimgdata = tk.PhotoImage(data=bgimgraw) # code for file with any dimensions.
bgimg = bgimgdata.zoom(1,1)
bgimg = bgimgdata.subsample(1,5)
# bgimg = tk.PhotoImage(file='link') # code for file with correct dimensions.

logoimgdata = tk.PhotoImage(data=logoimgraw)
logoimg = logoimgdata.subsample(5,5)

# Background Image
bgimglabel = tk.Label(main, image=bgimg, bg='lightgray', border=0)
bgimglabel.grid(column=0, row=0, columnspan=2)

# Profile frame (all of left) 
profileframe = tk.Frame(main, bg=PROFILEBG)
profileframe.grid(column=0, row=1, sticky='nsew')
profileframe.grid_columnconfigure(0, weight=0)
profileframe.grid_columnconfigure(1, weight=1)
profileframe.grid_rowconfigure(0, weight=0)
profileframe.grid_rowconfigure(1, weight=1)

logoimglabel = tk.Label(profileframe, image=logoimg, border=0)
logoimglabel.grid(column=0, row=0, padx=20, pady=20)

# Chat frame (all of right) 
mainchatframe = tk.Frame(main, bg=CHATBG)
mainchatframe.grid(column=1, row=1, sticky='nsew')
mainchatframe.columnconfigure(0, weight=1)
mainchatframe.columnconfigure(1, weight=1)
mainchatframe.rowconfigure(0, weight=1) # for the chat to fill
mainchatframe.rowconfigure(1, weight=0) # for the inputframe to remain same size

# Chat frame notebook
chattab = ttk.Notebook(mainchatframe)

chatframe1 = tk.Frame(chattab)
chatframe2 = tk.Frame(chattab)
chatframe3 = tk.Frame(chattab)
chatframe1.grid_columnconfigure(0, weight=1)
chatframe2.grid_columnconfigure(0, weight=1)
chatframe3.grid_columnconfigure(0, weight=1)

chattab.add(chatframe1, text="F1")
chattab.add(chatframe2, text="F2")
chattab.add(chatframe3, text="F3")
chattab.grid(column=0, row=0, columnspan=2, sticky='nsew', padx=20, pady=20)

# Input frame (bottom-right) 
inputframe = tk.Frame(mainchatframe, bg=TEXTBG)
inputframe.columnconfigure(0, weight=1)
inputframe.columnconfigure(1, weight=0)
inputframe.rowconfigure(0, weight=1)
inputframe.grid(column=0, row=1, columnspan=2, sticky='nsew')

# Textbox and send button
textbox = tk.Entry(inputframe, bg=TEXTBG, insertbackground='white', selectforeground=TEXTBG, fg='white')
textbox.grid(column=0, row=0, sticky='ew', padx=5, pady=10)
textbox.bind("<Return>", lambda event:sendMessage()) # allows pressing enter to chat
sendbtn = tk.Button(inputframe, text='Send', bg=TEXTBG, fg=TEXTBG, command=sendMessage)
sendbtn.grid(column=1, row=0, sticky='ew', pady=10, padx=(0,5))

main.withdraw()

#ELEMENTS
initialize = ttk.Notebook(root)

jointab = Frame(initialize)
joinlabel = Label(jointab, text="Welcome to tunnelNET!")
joinlabel2 = Label(jointab, text="Please enter your join key (tskey-auth):")
joinentry = Entry(jointab)
joinbutton = Button(jointab, text="Connect", command=join)

#this next chunk is for auth
if system == "Linux":
    authlevel = Toplevel(root)
    authlevel.resizable(FALSE,FALSE)
    authlevel.geometry("350x150+200+200")
    authentry = Entry(authlevel,show="*")
    authlabel = Label(authlevel, text="Welcome to tunnelNET, for the linux part this application needs sudo to communicate with the tailscale daemon. If you wish to use tunnelNET please enter sudo auth below.", wraplength=300)
    authbutton = Button(authlevel, text="Authenticate",command=sudofetch)

    authlevel.deiconify()
    authlabel.pack()
    authentry.pack()
    authbutton.pack()
    root.withdraw()


joinlabel.grid(column=1, row=0 ,sticky=NSEW)
joinlabel2.grid(column=1, row=1 ,sticky=NSEW)
joinentry.grid(column=1, row=2 ,sticky=EW)
joinbutton.grid(column=1, row=3 ,sticky=NSEW)

logintab = Frame(initialize)
introlabel = Label(logintab, text="Welcome to tunnelNET!")
loginlabel = Label(logintab, text="Login (OAuth ID): ")
passlabel = Label(logintab, text="Password (OAuth Secret)")
loginentry = Entry(logintab)
passentry = Entry(logintab)
loginbutton = Button(logintab, text="Login", command=login)

for bcol in range(3):
    logintab.columnconfigure(bcol, weight=1)
    jointab.columnconfigure(bcol, weight=1)
for crow in range(8):
    logintab.rowconfigure(crow, weight=1)
    jointab.rowconfigure(crow, weight=1)

initialize.add(logintab, text="Login")
initialize.add(jointab, text="Join")

introlabel.grid(column=1, row=0 ,sticky=NSEW)
loginlabel.grid(column=1, row=1, sticky = NSEW)
loginentry.grid(column=1,row=2, sticky=EW)
passlabel.grid(column=1, row=3, sticky=NSEW)
passentry.grid(column=1, row=4, sticky=EW)
loginbutton.grid(column=1, row=5, sticky=NSEW)

initialize.grid(row=0,column=0,rowspan=8,columnspan=3, sticky=NSEW)

try:
    with open(USERSAVEDIR, encoding="utf-8") as dingus:
        usersave = dingus.read()
        if usersave == "":
            print("Nothing found in usersave, skipping...")
        else:
            loginentry.insert(0, usersave)
except FileNotFoundError:
    print("usersave file not found, program confused. skipping...")
except Exception as error:
    print(error)


root.mainloop()
import platform 
import requests
import shlex
import subprocess
import atexit
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
import socket
import re
import json

#macbackend pull

userdir = Path(__file__).resolve()

system = platform.system()#OS CHECK STARTS HERE, should return "Windows", "Linux", or "Darwin" for MacOS.
#see official python documentation if confused.
#Nathan keep your code for the installscript inside an if statement checking variable system for OS thanks
CLIENTSECRET = ""
CLIENTID = ""
APIKEY = ""
TAILNET = ""
TAILNAME = ""
AUTH = ""
STDOUT = ""
SUDO = ""
ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
JSONFLAG = False
JSONDECODER = json.JSONDecoder()
JSON = ""
USERSAVEDIR = str(userdir.parent)+"/Assets/usersave.txt"
SUDOAUTH = False
ISHOST = False
ISLOG = False

#############
msg_queue = queue.Queue()
cmd_queue = queue.Queue()
MESG_PORT = 55554
chat_logs = {}
#############

#updated information (stuff that needs to be refreshed)
SELF = {}
DEVICES = {}
#tunnelnet should only save the clientID. APIKEY cannot be saved and 
#must be requested at user login.
#physical control of local API can be done using cli, my idea is to run
#a daemon thread to do all the terminal stuff using schlex.
if system == "Windows":
    try:
        from pexpect.popen_spawn import PopenSpawn
        inject = PopenSpawn("cmd.exe", encoding="utf-8")
    except (ImportError, Exception):
        inject = None
else:
    shell_path = "/bin/zsh" if system == "Darwin" else "/bin/bash"
    inject = pexpect.spawn(shell_path, encoding="utf-8")

if inject:
    inject.logfile = sys.stdout

import time # Needed for timestamps
def send_packet(target_ip, message):
    """
    Helper to queue a message for sending.
    """
    payload = {
        "destination": target_ip, # The user said "destination device name" but we need IP to connect
        "sender": TAILNAME or socket.gethostname(),
        "message": message,
        "timestamp": str(time.time())
    }
    msg_queue.put((target_ip, payload))
def login(): #login command.
    '''
    login function, works with the tailscale webAPI to claim an API key, and an auth key.
    '''
    global APIKEY,CLIENTID,CLIENTSECRET,ISHOST, ISLOG
    CLIENTID = loginentry.get()
    CLIENTSECRET = passentry.get()
    if CLIENTID == "" or CLIENTSECRET == "":
        print("Error: One or more authentication elements are missing!")
    elif CLIENTSECRET == "testing":
        print("login bypassed")
        root.withdraw()
        main.deiconify()
        refreshnet()
    else:
        status = requesttoken(CLIENTID, CLIENTSECRET)
        print(status)
        status2 = authkey(APIKEY)
        if status == 200 and status2 == 200:
            ISHOST = True
            try:
                with open(USERSAVEDIR, "w") as dingus2:
                    dingus2.write(CLIENTID)
                    print("saved id")
            except Exception as err:
                print(err)
            print("login successful")
            root.withdraw()
            main.deiconify()
        logassemble = f"tailscale up --auth-key={AUTH}"
        cmd_queue.put(logassemble)
        ISLOG = True


def join(): 
    '''
    for the join tab of the initialize window.
    '''
    global AUTH, ISHOST, ISLOG
    AUTH = joinentry.get()
    cmd_queue.put(f"tailscale up --auth-key={AUTH}")
    ISHOST = False
    ISLOG = True
    root.withdraw()
    main.deiconify()


def sudofetch(): 
    '''
    determine if sudo works and show next screen if successful.
    '''
    global SUDO, SUDOAUTH, JSONFLAG
    SUDO = authentry.get()
    if SUDO == "":
        print("Error: Nothing in authentication!")
    else:
        cmd_queue.put("echo success!")
        cmd_queue.join()
        # Give the worker thread time to authenticate
        import time
        time.sleep(1)
        if SUDOAUTH:
            authlevel.withdraw()
            root.deiconify()
            JSONFLAG = True
            cmd_queue.put("tailscale status --json")
            ###############################################continue here
            cmd_queue.join()
            if JSON["BackendState"] == "Running":
                initialize.add(softlogtab, text="Soft Login")
                softloglabel.grid(row=0, column=1, sticky=NSEW)
                softloglabel2.grid(row=1,column=1, sticky=NSEW)
                softlogbutton.grid(row=2,column=1,sticky=NSEW)
                

        else:
            print("sudo authentication failed, verify password...")

def bash_worker():
    global STDOUT, SUDO, inject, SUDOAUTH, JSONFLAG, JSONDECODER, JSON
    
    while True:
        cmd = cmd_queue.get()
        if cmd is None:
            break
        try:
            # Authenticate sudo ONCE at the start, not for every command
            if not SUDOAUTH:
                if system == "Windows":
                    # Windows doesn't use sudo in the same way; 
                    # for now, we assume the process has necessary rights
                    # or we could implement runas logic here.
                    SUDOAUTH = True 
                    print("Windows shell initialized")
                else:
                    try:
                        print(f"SUDO not detected on {system}! Injecting...")
                        inject.sendline("sudo -s")
                        inject.expect(r"[Pp]assword", timeout=5)
                        inject.sendline(SUDO)
                        # Mac/Linux prompts might differ; # is common for root
                        inject.expect([r"# ", r"\$ "], timeout=5)
                        SUDOAUTH = True
                        print("Sudo authenticated successfully")
                    except Exception as E:
                        print("sudError: ", E)
                        SUDOAUTH = False
            
            # Only send the command
            if system == "Windows":
                # For Windows commands, we might need a different echo or prompt check
                inject.sendline(cmd)
                # cmd.exe usually ends with >
                inject.expect(r">", timeout=5)
            else:
                inject.sendline(cmd)
                inject.expect([r"# ", r"\$ "], timeout=5)
            
            STDOUT = inject.before.split("\r\n", 1)[-1]
            STDOUT = ansi_escape.sub('', STDOUT).strip()
            if JSONFLAG == True:
                JSON, index = JSONDECODER.raw_decode(STDOUT)
                JSONFLAG = False

        except Exception as e:
            print("Worker error:", e)
        finally:
            cmd_queue.task_done()

def jsonhandler(bashcmd):
    '''
    simple function to handle json responses from bash worker. takes a json expecting bash command; all outputs translated to a dict in global JSON.
    '''
    global JSONFLAG
    print("json parse requested")
    JSONFLAG = True
    cmd_queue.put(bashcmd)

def refreshnet():
    '''
    function for refreshing all information relating to a user's tailnet (devices, ips, etc)
    '''
    global JSONFLAG, SELF, JSON, TAILNET, STDOUT, TAILNAME, DEVICES
    try:
        JSONFLAG = True
        cmd_queue.put("tailscale status --json")
        cmd_queue.join()
        if "Tailscale is stopped." in JSON["Health"]:
            print("tailscale service stopped... restarting...")
            cmd_queue.put("tailscale up")
            JSONFLAG = True
            cmd_queue.put("tailscale status --json")
            cmd_queue.join()
        TAILNAME = (JSON["CurrentTailnet"])["Name"]

        ##COMMAND SPECIFIC

        cmd_queue.put("tailscale status --json | jq -r \'.Peer[] | \"\\(.HostName) \\(.TailscaleIPs[0])\"\'")
        cmd_queue.join()

        STDOUT = STDOUT[:STDOUT.rfind("\r\n")]

        for char in "\r\n":
            STDOUT = STDOUT.replace(char, " ")
        assembly = STDOUT.split()
        toggle = 1
        obj1 = ""
        obj2 = ""

        for object in assembly:
            if toggle == 1:
                toggle = 2
                obj1 = object
            elif toggle == 2:
                toggle = 1
                obj2 = object
                DEVICES[obj1] = obj2
        print(len(DEVICES))
    except Exception as e:
        print("Error:", e)

    

def requesttoken(cid, cs):
    '''
    Requests an API key if the login function is called. input the preset oauth client id and client secret and output to APIKEY global.
    '''
    global APIKEY,CLIENTID,CLIENTSECRET
    token_url = "https://api.tailscale.com/api/v2/oauth/token"
    try:
        response = requests.post(
            token_url,
            data={"grant_type": "client_credentials"},
            auth=(cid, cs),
        )
        APIKEY = response.json()["access_token"]
    except KeyError:
        print(response.json()["message"])
    print("key requested: "+APIKEY)
    return response.status_code


def listdevices(apikey, tailnet = "-"):
    '''
    lists devices from the tailscale api.
    changes methods depending on whether the client has host access or local net access.
    use flag (ISHOST to create if clause.)
    '''
    if ISHOST == True:
        token_url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
        response = requests.get(
            token_url,
            headers= {'Authorization':f"Bearer {apikey}"}
        )
        print(response)
        print(response.json())
    else:
        JSONFLAG == True
        cmd_queue.put("tailscale status --json")

def authkey(apikey, tailnet = "-"):
    '''
    uses the apikey and fetches an authkey for the program.
    '''
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


def exitcatcher():
    print("exit triggered")
    cmd_queue.put("tailscale logout")

#BASH THREAD STARTER
bash_thread = threading.Thread(target=bash_worker, daemon=True)
bash_thread.start()

def messaging_service():
    """
    Handles sending, receiving, and acknowledging messages.
    """
    def listener():
        # TCP Listener Thread
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', MESG_PORT))
            s.listen()
            print(f"Messaging listener started on port {MESG_PORT}")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(4096).decode('utf-8')
                    if data:
                        try:
                            msg = json.loads(data)
                            sender = msg.get("sender", "Unknown")
                            channel = sender # early stage: channel name is sender name
                            
                            # Format for chatlog
                            # chat_logs[channel][timestamp] = {msg, sender, time, read}
                            if channel not in chat_logs:
                                chat_logs[channel] = {}
                            
                            timestamp = msg.get("timestamp", str(time.time()))
                            chat_logs[channel][timestamp] = {
                                "raw": msg.get("message", ""),
                                "sender": sender,
                                "timestamp": timestamp,
                                "read": False
                            }
                            
                            # ACK with a reply repeating and acknowledging the message
                            ack = {
                                "status": "ACK",
                                "received_msg": msg.get("message", ""),
                                "original_timestamp": timestamp,
                                "sender": TAILNAME or "LocalHost"
                            }
                            conn.sendall(json.dumps(ack).encode('utf-8'))
                            print(f"Message received from {sender}, ACK sent.")
                        except Exception as e:
                            print(f"Listener error: {e}")

    # Start the listener thread
    threading.Thread(target=listener, daemon=True).start()

    # Worker for sending messages
    while True:
        target_ip, payload = msg_queue.get()
        if target_ip is None: break
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((target_ip, MESG_PORT))
                s.sendall(json.dumps(payload).encode('utf-8'))
                
                # Wait for ACK
                ack_data = s.recv(4096).decode('utf-8')
                if ack_data:
                    ack = json.loads(ack_data)
                    print(f"Message acknowledged by {target_ip}: {ack.get('status')}")
                    # Update local log to show it was acknowledged? 
                    # User said "both devices should have acknowledged that the msg has been received"
        except Exception as e:
            print(f"Send error to {target_ip}: {e}")
        finally:
            msg_queue.task_done()

msg_thread = threading.Thread(target=messaging_service, daemon=True)
msg_thread.start()



atexit.register(exitcatcher)
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
main.columnconfigure(1, weight=10) # for mainchat
main.columnconfigure(0, weight=1) # for profile
main.rowconfigure(1, weight=10) # for chat
main.rowconfigure(0, weight=0) # for computer background image

# Colors (Can be changed in the future; just here for placeholder)
BANNERBG = "#131415"
PROFILEBG = "#1B1C1E"
CHATBG = "#2C2E31"
TEXTBG = "#32363B"
SELECTBG = "#6C727C"
SERVERBG = "#202124"

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
profileframe.grid_columnconfigure(2, weight=0)
profileframe.grid_rowconfigure(0, weight=0)
profileframe.grid_rowconfigure(1, weight=0)
profileframe.grid_rowconfigure(2, weight=0)
profileframe.grid_rowconfigure(3, weight=1)

logoimglabel = tk.Label(profileframe, image=logoimg, border=0)
logoimglabel.grid(column=0, row=0, padx=20, pady=20, rowspan=3)

namelabel = tk.Label(profileframe, text="Tunnelnet", font=("Arial", 20))
namelabel.grid(column=1, row=0)

userlabel = tk.Label(profileframe, text="Welcome, User", font=("Arial", 10))
userlabel.grid(column=1, row=1)

IPlabel = tk.Label(profileframe, text="Logged in from IP...", font=("Arial", 10))
IPlabel.grid(column=1, row=2)

# Server frame (users and other online people); part of Profileframe
serverframe = tk.Frame(profileframe, bg=SERVERBG)
serverframe.grid(column=0, row=3, columnspan=3, sticky='nsew')
serverframe.grid_columnconfigure(0, weight=1)
serverframe.grid_columnconfigure(1, weight=3)
serverframe.grid_columnconfigure(2, weight=0)
serverframe.grid_rowconfigure(0, weight=1)
serverframe.grid_rowconfigure(1, weight=5)
serverframe.grid_rowconfigure(2, weight=5)
serverframe.grid_rowconfigure(3, weight=5)

usertitlelabel = tk.Label(serverframe, text='Users', font=100)
usertitlelabel.grid(column=0, row=0, columnspan=2, sticky=NW, padx=20, pady=20)

# Chat frame (all of right) 
mainchatframe = tk.Frame(main, bg=CHATBG)
mainchatframe.grid(column=1, row=1, sticky='nsew')
mainchatframe.columnconfigure(0, weight=1)
mainchatframe.columnconfigure(1, weight=1)
mainchatframe.rowconfigure(0, weight=1) # for the chat to fill
mainchatframe.rowconfigure(1, weight=0) # for the inputframe to remain same size
mainchatframe.grid_propagate(False)

# Chat frame notebook
chattab = ttk.Notebook(mainchatframe)
chattabcount = 3
chatframes = []

chatframe1 = tk.Frame(chattab)
chatframe2 = tk.Frame(chattab)
chatframe3 = tk.Frame(chattab)
chattab.add(chatframe1, text="F1")
chattab.add(chatframe2, text="F2")
chattab.add(chatframe3, text="F3")

chatframes.extend([chatframe1, chatframe2, chatframe3]) #Puts chatframe1-3 into chatframes list
chattab.grid(column=0, row=0, columnspan=2, sticky='nsew', padx=20, pady=20)

for frames in (chatframes):
    frames.grid_columnconfigure(0, weight = 1)

def addchattab():
    global chattabcount
    if chattabcount < 20:
        chattabcount += 1
        newframe = tk.Frame(chattab)
        newframe.grid_columnconfigure(0, weight = 1)
        chattab.add(newframe, text=f"F{chattabcount}")
        chatframes.append(newframe)
        chattab.select(newframe)
    else:
        pass

addtabbtn = tk.Button(chattab, text='Add Chat', bg=SELECTBG, fg='white', activebackground=BANNERBG, activeforeground='black', relief='flat', width=2)
addtabbtn.config(command = addchattab)
addtabbtn.pack(side=LEFT, anchor=NW)

# Input frame (bottom-right) 
inputframe = tk.Frame(mainchatframe, bg=TEXTBG)
inputframe.columnconfigure(0, weight=1)
inputframe.columnconfigure(1, weight=0)
inputframe.rowconfigure(0, weight=1)
inputframe.grid(column=0, row=1, columnspan=2, sticky='nsew')

# Textbox and send button
textbox = tk.Entry(inputframe, bg=TEXTBG, insertbackground='white', selectbackground='white', fg='white')
textbox.grid(column=0, row=0, sticky='ew', padx=5, pady=10)
textbox.bind("<Return>", lambda event:sendMessage()) # allows pressing enter to chat
sendbtn = tk.Button(inputframe, text='Send', bg=TEXTBG, fg=TEXTBG, command=sendMessage)
sendbtn.grid(column=1, row=0, sticky='ew', pady=10, padx=(0,5))

# Other Functions
def resize_text(event):
    # Calculate new font size based on window width
    if event.widget == main:
        logo_size = max(20, int(event.width / 40))
        namelabel.config(font=("Arial", logo_size))
        userlabel.config(font=("Arial", int(logo_size/2)))
        IPlabel.config(font=("Arial", int(logo_size/3)))
main.bind("<Configure>", resize_text) # allows the resize gets detected

main.withdraw()

#ELEMENTS
initialize = ttk.Notebook(root)

jointab = Frame(initialize)
joinlabel = Label(jointab, text="Welcome to tunnelNET!")
joinlabel2 = Label(jointab, text="Please enter your join key (tskey-auth):")
joinentry = Entry(jointab)
joinbutton = Button(jointab, text="Connect", command=join)

def softlogfunc():
    root.withdraw()
    main.deiconify()
    refreshnet()

softlogtab = Frame(initialize)
softloglabel = Label(softlogtab, text="Welcome to tunnelNET!")
softloglabel2 = Label(softlogtab, text="The tailscale service was found to be logged in, if you want to login as a user instead of a host click login below, otherwise go to the login tab.", wraplength=300)
softlogbutton = Button(softlogtab,text="Login", command=softlogfunc)


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
    softlogtab.columnconfigure(bcol, weight=1)
for crow in range(8):
    logintab.rowconfigure(crow, weight=1)
    jointab.rowconfigure(crow, weight=1)
    softlogtab.rowconfigure(crow, weight=1)

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
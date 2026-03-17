import platform 
import requests
import shlex
import subprocess
import threading
import queue
from pathlib import Path
from tkinter import *
from tkinter import ttk
import tkinter as tk

userdir = Path(__file__).resolve()

system = platform.system()#OS CHECK STARTS HERE, should return "Windows", "Linux", or "Darwin" for MacOS.
#see official python documentation if confused.
#Nathan keep your code for the installscript inside an if statement checking variable system for OS thanks
CLIENTSECRET = ""
CLIENTID = ""
APIKEY = ""
TAILNET = ""
USERSAVEDIR = str(userdir.parent)+"/Assets/usersave.txt"
#tunnelnet should only save the clientID and clientSecret. APIKEY cannot be saved and 
#must be requested at user login.
#physical control of local API can be done using cli, my idea is to run
#a daemon thread to do all the terminal stuff using schlex.
def login():
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
        if status == 200:
            try:
                with open(USERSAVEDIR, "w") as dingus2:
                    dingus2.write(CLIENTID)
                    print("saved id")
            except Exception as err:
                print(err)
            print("login successful")
            root.withdraw()
            main.deiconify()
        logassemble = f"sudo tailscale up --auth-key={APIKEY}"
        cmd_queue.put(logassemble)

def bash_worker():
    while True:
        cmd = cmd_queue.get()
        if cmd is None:
            break
        try:
            args = shlex.split(cmd)
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("EXIT:", result.returncode)
                print(result.stdout)
                print("ERR:", result.stderr)

        except Exception as e:
            print("Worker error:", e)
        cmd_queue.task_done()



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

def getkeystatus(apikey):
    pass


cmd_queue = queue.Queue()
thread = threading.Thread(target=bash_worker, daemon=True)
thread.start()

if system == "Linux":
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
    #10rows 10columns
    for rwcl in range(10):
        main.rowconfigure(rwcl, weight=1)
        main.columnconfigure(rwcl, weight=1)
        
    main.withdraw()
    #ELEMENTS
    initialize = ttk.Notebook(root)

    jointab = Frame(initialize)
    joinlabel = Label(jointab, text="Welcome to tunnelNET!")
    joinlabel2 = Label(jointab, text="Please enter your join key (tskey-auth):")
    joinentry = Entry(jointab)
    joinbutton = Button(jointab, text="Connect", command=lambda:print("yeah yeah ill work on this later"))

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
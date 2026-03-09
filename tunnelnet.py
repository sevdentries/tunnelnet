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
    root = Tk()
    root.geometry("300x150+200+200")
    root.title("tunnelNET: Login")

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0 , weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=2)
    root.rowconfigure(3, weight=2)
    root.rowconfigure(4, weight=2)
    root.rowconfigure(5, weight=2)
    root.rowconfigure(6, weight=2)
    root.rowconfigure(7, weight=2)

    introlabel = Label(root, text="Welcome to tunnelNET!")
    loginlabel = Label(root, text="Login (OAuth ID): ")
    passlabel = Label(root, text="Password (OAuth Secret)")
    loginentry = Entry(root)
    passentry = Entry(root)
    loginbutton = Button(root, text="Login", command=login)

    introlabel.grid(column=1, row=0 ,sticky=NSEW)
    loginlabel.grid(column=1, row=1, sticky = NSEW)
    loginentry.grid(column=1,row=2, sticky=EW)
    passlabel.grid(column=1, row=3, sticky=NSEW)
    passentry.grid(column=1, row=4, sticky=EW)
    loginbutton.grid(column=1, row=5, sticky=NSEW)

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
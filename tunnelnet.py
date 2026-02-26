import platform 
import requests
import shlex
import subprocess
from tkinter import *
from tkinter import ttk
import tkinter as tk

system = platform.system()#OS CHECK STARTS HERE, should return "Windows", "Linux", or "Darwin" for MacOS.
#see official python documentation if confused.
#Nathan keep your code for the installscript inside an if statement checking variable system for OS thanks
CLIENTSECRET = ""
CLIENTID = ""
APIKEY = ""
#tunnelnet should only save the clientID and clientSecret. APIKEY cannot be saved and 
#must be requested at user login.
#physical control of local API can be done using cli, my idea is to run
#a daemon thread to do all the terminal stuff using schlex.


if system == "Linux":
    root = Tk()
    root.geometry("600x400+200+200")
    root.title("tunnelNET: Login")

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=1)

    introlabel = Label(Text)


root.mainloop()
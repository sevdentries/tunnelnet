import tkinter as tk
from tkinter import ttk
from tkinter import *
from urllib.request import urlopen
import webbrowser
import os

# Colors (Can be changed in the future; just here for placeholder)
BANNERBG = "#131415"
PROFILEBG = "#1B1C1E"
CHATBG = "#2C2E31"
TEXTBG = "#32363B"
SELECTBG = "#6C727C"
SERVERBG = "#202124"

# Variables
# placeholder

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
settingimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Assets/settings.png'
try:
    with urlopen(bgimglink) as img1:
        bgimgraw = img1.read()
    with urlopen(logoimglink) as img2:
        logoimgraw = img2.read()
except Exception as linkerror: 
    print("Fetch logo failed", str(linkerror))

# main start
main = tk.Tk()
main.geometry('600x400+100+100')
main.title('Tunnelnet')
main.configure(bg="lightgray")
main.columnconfigure(1, weight=10) # for mainchat
main.columnconfigure(0, weight=1) # for profile
main.rowconfigure(1, weight=10) # for chat
main.rowconfigure(0, weight=0) # for computer background image

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

SELF = {
    "John's Macbook Air": "192.168.0.1"
}

for user, ip in SELF.items():
    selfname = str(user)
    selfip = str(ip)

userlabel = tk.Label(profileframe, text=f"Welcome, {selfname}", font=("Arial", 10))
userlabel.grid(column=1, row=1)

IPlabel = tk.Label(profileframe, text=f"Logged in from IP {selfip}", font=("Arial", 10))
IPlabel.grid(column=1, row=2)

# Server frame (users and other online people); part of Profileframe
serverframe = tk.Frame(profileframe, bg=SERVERBG)
serverframe.grid(column=0, row=3, columnspan=3, sticky='nsew')
serverframe.grid_columnconfigure(0, weight=1)
serverframe.grid_columnconfigure(1, weight=3)
serverframe.grid_columnconfigure(2, weight=3)
serverframe.grid_rowconfigure(0, weight=1)
for i in range(100):
    serverframe.grid_rowconfigure(i+1, weight=2)

usertitlelabel = tk.Label(serverframe, text='Users Online', font=200)
usertitlelabel.grid(column=0, row=0, columnspan=2, sticky=NW, padx=20, pady=20)

DEVICES = {
    "laptop-1": "100.101.102.103",
    "phone-1": "100.104.105.106",
    "laptop-2": "256.101.102.103",
    "phone-2": "103.104.105.106",
    "laptop-3": "196.168.102.103",
    "phone-3": "1.1.1.1",
    }

USERrow = 1
for user, ip in DEVICES.items():
    DEVICElabel = tk.Label(serverframe, text=str(user), font=("Arial", 12))
    DEVICElabel.grid(column=1, row=USERrow, sticky="w")

    IPDEVICElabel = tk.Label(serverframe, text=str(ip), font=("Arial", 12))
    IPDEVICElabel.grid(column=2, row=USERrow, sticky="w")
    USERrow += 1

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

# Temporary testing code
# N/A

main.mainloop()

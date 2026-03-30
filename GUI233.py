import tkinter as tk
from tkinter import ttk
from urllib.request import urlopen
import webbrowser
import os

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
bgimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Assets/computerBackground.png'
logoimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Assets/tunnel.png'
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
main.columnconfigure(1, weight=3) # for mainchat
main.columnconfigure(0, weight=1) # for profile
main.rowconfigure(1, weight=10) # for chat
main.rowconfigure(0, weight=0) # for computer background image

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

# Temporary testing code
# N/A

main.mainloop()

import tkinter as tk
from tkinter import ttk
from urllib.request import urlopen
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
import os

# Colors (Can be changed in the futurel; just here for placeholder)
BANNERBG = "#131415"
PROFILEBG = "#1B1C1E"
CHATBG = "#2C2E31"
TEXTBG = "#32363B"
SELECTBG = "#6C727C"

# Commands
def onClick():
    input = textbox.get()
    result = f'You inputted {input}'
    message.configure(text = result)

# Image loading
bgimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Asset/computerBackground.png'
logoimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Asset/tunnel.png'
try:
    with urlopen(bgimglink) as img1:
        bgimgdata = BytesIO(img1.read())
    with urlopen(logoimglink) as img2:
        logoimgdata = BytesIO(img2.read())
except Exception as lerror: 
    print("Fetch logo failed", str(lerror))

# Root start
root = tk.Tk()
root.geometry('1470x956')
root.title('Tunnelnet')
root.configure(bg="lightgray")
root.columnconfigure(2, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=0)
root.rowconfigure(1, weight=1) # only row 1 can fill 
root.rowconfigure(0, weight=0)

# Images variables
resized_bgimg = Image.open(bgimgdata)
resized_bgimg = resized_bgimg.resize((1470, 200))
resized_logoimg = Image.open(logoimgdata)
resized_logoimg = resized_logoimg.resize((100, 100))
bgimg = ImageTk.PhotoImage(resized_bgimg)
logoimg = ImageTk.PhotoImage(resized_logoimg)

# Images
bgimglabel = tk.Label(image=bgimg, bg='lightgray', border=0)
bgimglabel.grid(column=0, row=0, sticky='n')

# Profile frame (all of left) 
profileframe = tk.Frame(root, bg=PROFILEBG, width=367.5)
profileframe.grid(column=0, row=1, sticky='wns')
profileframe.grid_columnconfigure(0, weight=0)
profileframe.grid_columnconfigure(1, weight=1)
profileframe.grid_rowconfigure(0, weight=0)
profileframe.grid_rowconfigure(1, weight=1)
profileframe.grid_propagate(False) # stops frame from disappearing

logoimglabel = tk.Label(profileframe, image=logoimg, border=0)
logoimglabel.grid(column=0, row=0, padx=20, pady=20)

# Chat frame (all of right) 
mainchatframe = tk.Frame(root, bg=CHATBG, width=1102.5)
mainchatframe.grid(column=0, row=1, sticky='ens')
mainchatframe.rowconfigure(0, weight=1) # for the chat (fills to fit)
mainchatframe.rowconfigure(1, weight=0) # for the inputframe (fixed width)
mainchatframe.grid_propagate(False) # stops frame from disappearing

# Input frame (bottom-right) 
inputframe = tk.Frame(mainchatframe, bg=TEXTBG, width=1102.5, height=20)
inputframe.grid(column=0, row=1, sticky='es')

# Textbox and send button
textbox = tk.Entry(inputframe, width=112, bg=TEXTBG, insertbackground='white', selectforeground=TEXTBG, fg='white')
textbox.grid(column=0, row=0, sticky='es', padx = (5, 5), pady=10)
sendbtn = tk.Button(inputframe, text='Send', bg=TEXTBG, fg=TEXTBG, command=onClick)
sendbtn.grid(column=1, row=0, pady=10, padx=(0,5))

# temporary testing code
message = tk.Label(mainchatframe, text='Send a message to update me!', bg='blue', fg='white')
message.grid(column=0, row=0)

root.mainloop()
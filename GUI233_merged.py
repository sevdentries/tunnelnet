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
bgimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Asset/computerBackground.png'
logoimglink = 'https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/Asset/tunnel.png'
try:
    with urlopen(bgimglink) as img1:
        bgimgraw = img1.read()
    with urlopen(logoimglink) as img2:
        logoimgraw = img2.read()
except Exception as linkerror: 
    print("Fetch logo failed", str(linkerror))

# main start
main = tk.Tk()
main.geometry('1470x956')
main.title('Tunnelnet')
main.configure(bg="lightgray")
main.columnconfigure(2, weight=1)
main.columnconfigure(1, weight=1)
main.columnconfigure(0, weight=1)
main.rowconfigure(2, weight=0)
main.rowconfigure(1, weight=1) # only row 1 can fill 
main.rowconfigure(0, weight=0)

# Images variables
bgimgdata = tk.PhotoImage(data=bgimgraw) # code for file with any dimensions.
bgimg = bgimgdata.zoom(1,5)
bgimg = bgimgdata.subsample(1,6)
# bgimg = tk.PhotoImage(file='link') # code for file with correct dimensions.

logoimgdata = tk.PhotoImage(data=logoimgraw)
logoimg = logoimgdata.subsample(5,5)

# Background Image
bgimglabel = tk.Label(image=bgimg, bg='lightgray', border=0)
bgimglabel.grid(column=0, row=0, sticky='n')

# Profile frame (all of left) 
profileframe = tk.Frame(main, bg=PROFILEBG, width=367.5)
profileframe.grid(column=0, row=1, sticky='wns')
profileframe.grid_columnconfigure(0, weight=0)
profileframe.grid_columnconfigure(1, weight=1)
profileframe.grid_rowconfigure(0, weight=0)
profileframe.grid_rowconfigure(1, weight=1)
profileframe.grid_propagate(False) # stops frame from disappearing

logoimglabel = tk.Label(profileframe, image=logoimg, border=0)
logoimglabel.grid(column=0, row=0, padx=20, pady=20)

# Chat frame (all of right) 
mainchatframe = tk.Frame(main, bg=CHATBG, width=1102.5)
mainchatframe.grid(column=0, row=1, sticky='ens')
mainchatframe.rowconfigure(0, weight=1) # for the chat (fills to fit)
mainchatframe.rowconfigure(1, weight=0) # for the inputframe (fixed width)
mainchatframe.grid_propagate(False) # stops frame from disappearing

# Chat frame notebook
chattab = ttk.Notebook(mainchatframe)
chattab.grid_propagate(False)

chatframe1 = tk.Frame(chattab, width=750, height=500)
chatframe2 = tk.Frame(chattab, width=750, height=500)
chatframe3 = tk.Frame(chattab, width=750, height=500)
chatframe1.grid_columnconfigure(0, weight=1)
chatframe2.grid_columnconfigure(0, weight=1)
chatframe3.grid_columnconfigure(0, weight=1)
chatframe1.grid_propagate(False)
chatframe2.grid_propagate(False)
chatframe3.grid_propagate(False)

chattab.add(chatframe1, text="F1")
chattab.add(chatframe2, text="F2")
chattab.add(chatframe3, text="F3")

chattab.grid(column=0, row=0)

# Input frame (bottom-right) 
inputframe = tk.Frame(mainchatframe, bg=TEXTBG, width=1102.5, height=20)
inputframe.grid(column=0, row=1, sticky='es')

# Textbox and send button
textbox = tk.Entry(inputframe, width=112, bg=TEXTBG, insertbackground='white', selectforeground=TEXTBG, fg='white')
textbox.grid(column=0, row=0, sticky='es', padx = (5, 5), pady=10)
textbox.bind("<Return>", lambda event:sendMessage()) # allows pressing enter to chat
sendbtn = tk.Button(inputframe, text='Send', bg=TEXTBG, fg=TEXTBG, command=sendMessage)
sendbtn.grid(column=1, row=0, pady=10, padx=(0,5))

# Temporary testing code
# N/A

main.mainloop()
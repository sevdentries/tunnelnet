from tkinter import *
from urllib.request import urlopen
from PIL import Image, ImageTk
import webbrowser
import os

root = Tk()
root.geometry('1470x956')
root.title('tunnel')

root.configure(bg="lightgray")
# root.columnconfigure(5, weight=1)
# root.columnconfigure(4, weight=1)
# root.columnconfigure(3, weight=1)
# root.columnconfigure(2, weight=1)
# root.columnconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
# root.rowconfigure(7, weight=1)
# root.rowconfigure(6, weight=1)
# root.rowconfigure(5, weight=1)
# root.rowconfigure(4, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(0, weight=3)

def onClick():
    input = txtbox.get()
    if input == 'meshmilk':
        label.configure(text = 'meshmilk!!!')
    else:
        result = f'You inputted {input}.'
        label.configure(text = result)

img1link = "https://raw.githubusercontent.com/sevdentries/tunnelnet/refs/heads/frontend/asset/computerBackground.png"

try:
    with urlopen(img1link) as image:
        img1data = image.read() 
except Exception as lerror: 
    print("Fetch logo failed", str(lerror))

img1 = PhotoImage(data=img1data)
img1label = Label(root, image=img1, bg='lightgray')
img1label.grid(column=0, row=0)

label = Label(root, text='Type something', bg='lightgray')
label.grid(column=0, row=1)

txtbox = Entry(root, width=10)
txtbox.grid(column=0, row=2)

startbtn = Button(root, text='Start', command=onClick)
startbtn.grid(column=0, row=3)

root.mainloop()
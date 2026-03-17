from tkinter import *
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("tab testing")
root.geometry("600x500")
maintab = ttk.Notebook(root)

frame1 = Frame(maintab, width=500, height=300)
frame2 = Frame(maintab, width=500, height=300)
frame3 = Frame(maintab, width=500, height=300)

a = Label(frame1, text="this is frame 1")
b = Label(frame2, text="this is frame 2")
c = Label(frame3, text="this is frame 3")

for i in range(9):
    frame1.rowconfigure(i, weight=1)
    frame2.rowconfigure(i, weight=1)
    frame3.rowconfigure(i, weight=1)
    frame1.columnconfigure(i, weight=1)
    frame2.columnconfigure(i, weight=1)
    frame3.columnconfigure(i, weight=1)

a.grid(row=4, column=4, sticky=NSEW)
b.grid(row=4, column=4, sticky=NSEW)
c.grid(row=4, column=4, sticky=NSEW)

# maintab.add(frame1, text="F1")
# maintab.add(frame2, text="F2")
# maintab.add(frame3, text="F3")

for mt in range(10):
    root.rowconfigure(mt, weight=1)
    root.columnconfigure(mt, weight=1)

maintab.grid(row=0, column=0, sticky=NSEW,columnspan=10,rowspan=10)

root.mainloop()
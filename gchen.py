import tkinter as tk
from tkinter import *
root = Tk()
root.geometry("500x500")
root.title("jaydon chan")
def open():
    window = tk.Toplevel(root)
    windowLabel = Label(window, text = "we love jaydon chan")
    testImage = PhotoImage(root, file = "Hi.png")
    imageLabel = Label(root, image=testImage)
    imageLabel.place(x=0,y=0)
   # windowLabel.
def greetFunction():
    i = altonEntry.get()
    responseLabel = Label(root, text = i)
    responseLabel.pack()
    



altonLabel = Label(root,text="Greetings, jaydon chan haven't seen u in ages",  font = ("Arial",12))
altonEntry = Entry(root, text="enter response here")
altonButton = Button(root, text="greet", command = greetFunction)
openButton = Button(root, text = "open things", command = open)


altonLabel.pack()
altonEntry.pack()
altonButton.pack()
openButton.pack()
root.mainloop()#start


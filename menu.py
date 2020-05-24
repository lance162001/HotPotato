from tkinter import *
from PIL import Image, ImageTk

RESOLUTIONS = [
"1024x576",
"1152x648",
"1280x720",
"1366x768",
"1600x900",
"1920x1080"
]
play=False
def run():
    if resolution.get() != "Resolution":
        global play
        play=True
        print("play button clicked...")
        master.destroy()    
    
master = Tk()
master.title("Menu")
master.geometry("550x190")

try:
    master.iconbitmap('assets\\icon.ico')
except:
    master.iconbitmap('Assets/icon.ico')


#Title
l = Label(master, text="Hot Potato", font=("Helvetica",24), pady=5)
l.pack()

l2 = Label(master, text="WASD or Arrow Keys to move, don't fall off the screen!", font=("Helvetica",14),pady=0)
l2.pack() 


resolution = StringVar(master)

resolution.set("Resolution") # default value

#Resolution Dropdown
w = OptionMenu(master, resolution, *RESOLUTIONS)
w.pack()

#Fullscreen Checkbox
fullscreen=IntVar(master)
c = Checkbutton(master, text="fullscreen", variable=fullscreen)
c.pack()

#Debugger Checkbox
debugger=IntVar(master)
d = Checkbutton(master, text="debugging", variable=debugger)
d.pack()

#Play Button
b = Button(master, text="Play", padx=10, command=run, bg = "#fe8761", fg = "#fff", activebackground="#af460f")
b.pack()

defs = open("defaults.txt", "r").read().split("\n")
resolution.set(defs[0].split("=")[1])
if defs[1].split("=")[1] == "True":
    c.select()
if defs[2].split("=")[1] == "True":
    d.select()




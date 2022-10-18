from tkinter import *

class App:
    def __init__(self,master):
       master.title('Python Canvas Testing')
       master.minsize(width=550, height=450)

       settingscanvas = Canvas(master,bg="yellow")
       settingscanvas.grid(sticky='ew')

       datacanvas = Canvas(master,bd=1,bg="green")
       datacanvas.grid(sticky='nsew')

       master.grid_rowconfigure(1,weight=1)
       master.grid_columnconfigure(0, weight=1)

       for r in range(15):
          Label(settingscanvas, text='Label'+str(r+1)).grid()

       Label(datacanvas, text='Label 2').grid()

## create main program window
window = Tk()

## create window container
app = App(window)

mainloop()
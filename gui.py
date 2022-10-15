import tkinter
from PIL import Image
from PIL import ImageTk
import cv2



def select_image():
    global panelA, panelB
    
    path = tkinter.filedialog()

    if len(path) > 0:
        image = cv2.imread(path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(image)
        edged = Image.fromarray(edged)
        # ...and then to ImageTk format
        image = ImageTk.PhotoImage(image)
        edged = ImageTk.PhotoImage(edged)

    if panelA is None or panelB is None:
        panelA = tkinter.Label(image=image)
        panelA.image = image
        panelA.pack(side="left", padx=10, pady=10)
        panelB = tkinter.Label(image=edged)
        panelB.image = edged
        panelB.pack(side="right", padx=10, pady=10)
    else:
        panelA.configure(image=image)
        panelB.configure(image=edged)
        panelA.image = image
        panelB.image = edged

def main():
    root = tkinter.Tk()
    panelA = None
    panelB = None
    btn = tkinter.Button(root, text="Select an image", command=select_image)
    btn.pack(side="bottom", fill="both", expand="yes", padx="10", pady="10")
    root.mainloop()

if __name__ == '__main__':
    main()
# m = tk.Tk()
# m.title('Field Prism')

# button = tk.Button(m, text='Stop', width=25, command=m.destroy)
# button.pack()

# m.mainloop()
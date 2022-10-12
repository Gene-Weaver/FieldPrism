from sshkeyboard import listen_keyboard

def press(key):
    print(f"'{key}' pressed")

def release(key,keypress):
    print(f"'{key}' released")
    selection(key,keypress)

    
def selection(key,keypress):
    if key == '1':
        keypress.photo = True
        print(f"keypress.photo == True'{key}'")
    elif key == '6':
        keypress.stop_all = True
        print(f"keypress.stop_all == True'{key}'")

class KeyPress:
    def __init__(self, name):
        self.photo = False
        self.stop_all = False

keypress = KeyPress
while True:
    listen_keyboard(on_press=press, on_release=release(keypress))

    if keypress.stop_all:
        break
    elif keypress.photo:
        print("PHOTO TIME!!!!!!!!!!!!!")
from pynput.keyboard import Key, Listener, KeyCode

def print_key(*key): ## prints key that is pressed
# key is a tuple, so access the key(char) from key[1]
    if key[1] == KeyCode.from_char('d'):
        print('yes!')

def key(): ## starts listener module
    with Listener(on_press=print_key) as listener:
        listener.join()

while True:
    key()
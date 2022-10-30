#!/usr/bin/env python3
'''
Function to animate "Ready" in the GUI
Updates each time the camera sends a photo to the "check focus" window
'''
def change_ready_ind(n,direction):
    to_out = '>'
    to_in = '<'
    if n == 10:
        direction='down'
        pick = to_in
        n -= 1
    elif n == 0:
        direction='up'
        pick = to_out
        n += 1
    else:
        if direction == 'up':
            pick = to_out
            n += 1
        else:
            pick = to_in
            n -= 1
    m = 10-n
    right = ''.join([char*m for char in pick])
    left = ''.join([char*n for char in pick])

    text_ready = ''.join([left,' Ready ',right])

    return text_ready, n, direction

def init_ready():
    ind_ready = 0
    direction ='up'
    return ind_ready, direction
'''
Mount USB drive/s to media/USB1 and media/USB2
calls mount_usb_drives.sh
'''
import subprocess

def mount_usb():
    result = subprocess.run(["sh", "./mount_usb_drives.sh"], stderr=subprocess.PIPE, text=True)
    print(result.stderr) # normal to see an error if this is printed, but usually there is no concern
    # will see the following if drives have never been mounted due to calling pumount(), that's what we want
    #        Error: device /dev/sda1 is not mounted
    #        Error: device /dev/sdb1 is not mounted

if __name__ == '__main__':
    mount_usb()
'''
Mount USB drive/s to media/USB1 and media/USB2
calls mount_usb_drives.sh
'''
import subprocess

def mount_usb():
    result = subprocess.run(["sh", "./mount_usb_drives.sh"], stderr=subprocess.PIPE, text=True)
    print(result.stderr)

if __name__ == '__main__':
    mount_usb()
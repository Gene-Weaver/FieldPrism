#!/bin/bash

# Check if the script is being run with root privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "This script needs to be run with root privileges. Please use sudo or run as root."
    exit 1
fi

# Check if the raspi-config package is installed
if ! dpkg -s raspi-config >/dev/null 2>&1; then
    echo "raspi-config package is not installed. Please install it using 'sudo apt-get install raspi-config' and try again."
    exit 1
fi

# Run raspi-config with the non-interactive flag to launch the tool
raspi-config nonint do_change_timezone

# Check the exit status of raspi-config
if [ $? -eq 0 ]; then
    echo "Timezone changed successfully."
else
    echo "Failed to change the timezone."
fi
echo ""
echo "This window will automatically close in 10 seconds..."
sleep 10
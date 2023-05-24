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

# Prompt the user to select the Wi-Fi country
echo "Available Wi-Fi country options:"
raspi-config nonint get_wifi_country | awk -F "[()]" '{ print $2 }'
read -p "Enter the Wi-Fi country code (e.g., HR for Croatia): " wifi_country

# Set the Wi-Fi country using raspi-config
raspi-config nonint do_wifi_country "$wifi_country"

# Prompt the user to select the timezone
echo "Available timezone options:"
raspi-config nonint get_current_timezone
read -p "Enter the timezone (e.g., Europe/Zagreb): " timezone

# Set the timezone using raspi-config
raspi-config nonint do_change_timezone "$timezone"

# Check the exit status of raspi-config
if [ $? -eq 0 ]; then
    echo "Wi-Fi country and timezone updated successfully."
else
    echo "Failed to update Wi-Fi country and timezone."
fi

echo ""
echo "This window will automatically close in 10 seconds..."
sleep 10
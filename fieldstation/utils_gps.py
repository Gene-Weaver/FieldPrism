#!/usr/bin/env python3
import time
from gps3.agps3threaded import AGPS3mechanism
from dataclasses import dataclass
from utils import bcolors, get_datetime

'''
Reference this guide for help:
    https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi/setting-everything-up
To see raw data from GPS module, in terminal:
    sudo cat /dev/ttyUSB0

    cgps -s

    - restart and test (read above url FIRST!)
    sudo killall gpsd
    sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock

    sudo systemctl stop gpsd.socket
    sudo systemctl disable gpsd.socket

    sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock


See the section: 
    CORE PROTOCOL RESPONSES ==> TPV
    https://gpsd.gitlab.io/gpsd/gpsd_json.html
for more info about each parameter
'''

@dataclass
class GPSPacket:
    current_time: float = -999
    latitude: float = -999
    longitude: float = -999    
    
    altitude: float = -999
    climb: float = -999
    speed: float = -999

    lat_error_est: float = -999
    lon_error_est: float = -999
    alt_error_est: float = -999

    def print_report(self,opt,do_print) -> None:
        if do_print:
            if opt == 'Pass':        
                print(f"{bcolors.GREENBG}       GPS REPORT{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.OKGREEN}       Time: {str(self.current_time)}{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.OKGREEN}       Latitude: {str(self.latitude)}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Longitude: {str(self.longitude)}{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.OKGREEN}       Altitude (m): {str(self.altitude)}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Climb: {str(self.climb)}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Speed: {str(self.speed)}{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.OKGREEN}       Lat error estimate: {self.lat_error_est}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Lon error estimate: {self.lon_error_est}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Alt error estimate: {self.alt_error_est}{bcolors.ENDC}")
                print(f"")
            elif opt == 'Fail':
                print(f"{bcolors.REDBG}       GPS REPORT -- GPS UNAVAILABLE{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.FAIL}       Time: {str(self.current_time)}{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.FAIL}       Latitude: {str(self.latitude)}{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Longitude: {str(self.longitude)}{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.FAIL}       Altitude (m): {str(self.altitude)}{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Climb: {str(self.climb)}{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Speed: {str(self.speed)}{bcolors.ENDC}")
                print(f"")
                print(f"{bcolors.FAIL}       Lat error estimate: {self.lat_error_est}{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Lon error estimate: {self.lon_error_est}{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Alt error estimate: {self.alt_error_est}{bcolors.ENDC}")
                print(f"")

def gps_activate(label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,use_data,do_print):
    print(f"       GPS Activated")
    if use_data:
        label_gps_status.config(text = 'GPS Activated', fg='orange')
        GPS_data = get_gps(cfg_user['fieldstation']['gps']['speed'],do_print)
        if GPS_data.latitude == -999:
            label_gps_status.config(text = 'No GPS Signal!', fg='red')
            label_gps_lat_status.config(text = 'Fail', fg='red')
            label_gps_lon_status.config(text = 'Fail', fg='red')
            label_gps_time_status.config(text = 'Not Available', fg='red')
            label_local_time_status.config(text = get_datetime(), fg='white') 
        else:
            label_gps_status.config(text = 'Good Signal', fg='green')
            label_gps_lat_status.config(text = str(GPS_data.latitude), fg='green')
            label_gps_lon_status.config(text = str(GPS_data.longitude), fg='green')
            label_gps_time_status.config(text = str(GPS_data.current_time), fg='green')
            label_local_time_status.config(text = get_datetime(), fg='white') 
    else:
        label_gps_status.config(text = 'Testing GPS Signal - Failing', fg='orange')
        GPS_data = get_gps(cfg_user['fieldstation']['gps']['speed'],do_print)
        if GPS_data.latitude == -999:
            print('************************************************************')
            label_gps_status.config(text = 'Testing GPS Signal - Failing', fg='orange')
            label_gps_lat_status.config(text = 'Failing', fg='orange')
            label_gps_lon_status.config(text = 'Failing', fg='orange')
            label_gps_time_status.config(text = 'Not Available', fg='red')
            label_local_time_status.config(text = get_datetime(), fg='white') 
        else:
            label_gps_status.config(text = 'Testing GPS Signal - Pass', fg='green')
            label_gps_lat_status.config(text = str(GPS_data.latitude), fg='green')
            label_gps_lon_status.config(text = str(GPS_data.longitude), fg='green')
            label_gps_time_status.config(text = str(GPS_data.current_time), fg='green')
            label_local_time_status.config(text = get_datetime(), fg='white') 
    return GPS_data

def update_GPS_data(data_stream, item):
    if data_stream.TPV[item] is not None:
        print(data_stream.TPV[item])

def get_gps(speed,do_print):
    if speed == 'fast':
        max_count = 3
    elif speed == 'cautious':
        max_count = 10
    GPS_data = GPSPacket()

    agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
    agps_thread.stream_data()  # From localhost (), or other hosts, by example, (host='gps.ddns.net')
    agps_thread.run_thread()  # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second

    count = 0
    count_fail = 0
    do_get_GPS = True
    take_data = False
    
    while do_get_GPS:  
        
        # line #140-ff of /usr/local/lib/python3.5/dist-packages/gps3/agps.py
        # time.sleep(0.1) # Sleep, or do other things for as long as you like.
        if (agps_thread.data_stream.lat != 'n/a') and (len(str(agps_thread.data_stream.lat).split('.')[1]) >= 3):
            # print('YES')
            count += 1
        else:
            # print('No')
            count_fail += 1
            time.sleep(0.05)
        
        if count > max_count:
            # print('SUCCESS')
            take_data = True
            do_get_GPS = False

        if count_fail > 20:
            do_get_GPS = False
            if GPS_data.latitude == -999:
                GPS_data.print_report('Fail',do_print)
            else:
                GPS_data.print_report('Pass',do_print)

        if take_data:
            GPS_data.latitude = agps_thread.data_stream.lat
            GPS_data.longitude = agps_thread.data_stream.lon
            GPS_data.altitude= agps_thread.data_stream.alt
            GPS_data.current_time = agps_thread.data_stream.time
            GPS_data.climb = agps_thread.data_stream.climb
            GPS_data.speed = agps_thread.data_stream.speed
            GPS_data.lat_error_est = agps_thread.data_stream.epy
            GPS_data.lon_error_est = agps_thread.data_stream.epx
            GPS_data.alt_error_est = agps_thread.data_stream.epv
            GPS_data.print_report('Pass',do_print)
        else:
            # Set the time to the R Pi's local time
            GPS_data.current_time = get_datetime()

    return GPS_data

if __name__ == '__main__':
    start = time.perf_counter()
    get_gps('fast',do_print=True)
    end = time.perf_counter()
    print(f"{bcolors.HEADER}GPS Fast: {round(end-start,5)} sec.{bcolors.ENDC}")
    print(f"")

    start = time.perf_counter()
    get_gps('cautious',do_print=True)
    end = time.perf_counter()
    print(f"{bcolors.HEADER}GPS Cautious: {round(end-start,5)} sec.{bcolors.ENDC}")
    print(f"")
    print("This window will automatically close in 5 seconds...")
    time.sleep(5)
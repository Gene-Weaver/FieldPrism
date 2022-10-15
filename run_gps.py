'''
Reference this guide for help:
    https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi/setting-everything-up
To see raw data from GPS module, in terminal:
    sudo cat /dev/ttyUSB0
'''
# import gps

# # Listen on port 2947 (gpsd) of localhost
# session = gps.gps("localhost", "2947")
# session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# while True:
#     try:
#         report = session.next()
#         # Wait for a 'TPV' report and display the current time
#         # To see all report data, uncomment the line below
#         # print(report)
#         if report['class'] == 'TPV':
#             if hasattr(report, 'time'):
#                 print(report.time)
#     except KeyError:
#         pass
#     except KeyboardInterrupt:
#         quit()
#     except StopIteration:
#         session = None
#         print("GPSD has terminated")
from dataclasses import dataclass
import time
from gps3 import gps3
from utils import bcolors

'''
See the section: 
    CORE PROTOCOL RESPONSES ==> TPV
    https://gpsd.gitlab.io/gpsd/gpsd_json.html
for more info about each parameter
'''
@dataclass
class GPSPacket:
    time: float = -999
    device: float = -999
    mode: float = -999
    mode_plain: float = -999

    latitude: float = -999
    longitude: float = -999    
    
    altitude: float = -999
    climb: float = -999
    speed: float = -999

    lat_error_est: float = -999
    lon_error_est: float = -999
    alt_error_est: float = -999
    
    def print_report():
        print(f"{bcolors.OKGREEN}GPS Report{bcolors.ENDC}")
        print(f"")
        print(f"{bcolors.OKGREEN}     Lat: {bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}     Lat: {bcolors.ENDC}")
        print(f"")
        print(f"{bcolors.OKGREEN}     Altitude (m): {bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}     Climb: {bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}     Speed: {bcolors.ENDC}")
        print(f"")
        print(f"{bcolors.OKGREEN}     Climb: {bcolors.ENDC}")


def get_gps():
    GPS_data = GPSPacket()

    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            print(data_stream)
            print('Altitude = ', data_stream.TPV['alt'])
            print('Latitude = ', data_stream.TPV['lat'])
            print('Longitude = ', data_stream.TPV['lon'])
            print('device = ', data_stream.TPV['device'])
            print('mode = ', data_stream.TPV['mode'])
            print('time = ', data_stream.TPV['time'])
            print('climb = ', data_stream.TPV['climb'])
            print('Longitude error estimate = ', data_stream.TPV['epx'])
            print('Latitude error estimate = ', data_stream.TPV['epy'])
            print('Estimated vertical error = ', data_stream.TPV['epv'])
            print('speed = ', data_stream.TPV['speed'])

if __name__ == '__main__':
    get_gps()
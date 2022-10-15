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
from gps3.agps3threaded import AGPS3mechanism
from utils import bcolors

'''
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

    def print_report(self,opt) -> None:
        if opt == 'Pass':        
            print(f"{bcolors.OKGREEN}GPS Report{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.OKGREEN}     Time: {str(self.current_time)}{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.OKGREEN}     Latitude: {str(self.latitude)}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}     Longitude: {str(self.longitude)}{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.OKGREEN}     Altitude (m): {str(self.altitude)}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}     Climb: {str(self.climb)}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}     Speed: {str(self.speed)}{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.OKGREEN}     Lat error estimate: {self.lat_error_est}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}     Lon error estimate: {self.lon_error_est}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}     Alt error estimate: {self.alt_error_est}{bcolors.ENDC}")
        elif opt == 'Fail':
            print(f"{bcolors.FAIL}GPS Report{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.FAIL}     Time: {str(self.current_time)}{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.FAIL}     Latitude: {str(self.latitude)}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}     Longitude: {str(self.longitude)}{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.FAIL}     Altitude (m): {str(self.altitude)}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}     Climb: {str(self.climb)}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}     Speed: {str(self.speed)}{bcolors.ENDC}")
            print(f"")
            print(f"{bcolors.FAIL}     Lat error estimate: {self.lat_error_est}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}     Lon error estimate: {self.lon_error_est}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}     Alt error estimate: {self.alt_error_est}{bcolors.ENDC}")
            print(f"")

def update_GPS_data(data_stream, item):
    if data_stream.TPV[item] is not None:
        print(data_stream.TPV[item])

def get_gps(speed):
    if speed == 'fast':
        max_count = 3
    elif speed == 'cautious':
        max_count = 10
    GPS_data = GPSPacket()

    # gps_socket = gps3.GPSDSocket()
    # data_stream = gps3.DataStream()
    # gps_socket.connect()
    # gps_socket.watch()

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
        if agps_thread.data_stream.lat != 'n/a':
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
            # print('ENDING')
            do_get_GPS = False
            GPS_data.print_report('Fail')

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
            GPS_data.print_report('Pass')
        if speed == 'cautious':
            time.sleep(0.1)
    return GPS_data
        


    
    # for new_data in gps_socket:
    #     if new_data:
    #         for count in range(0,10):
    #             print(f'Try {count}')
    #             data_stream.unpack(new_data)

    #             update_GPS_data(data_stream, 'lat')
    #             update_GPS_data(data_stream, 'lon')
    #             update_GPS_data(data_stream, 'alt')
    #             update_GPS_data(data_stream, 'time')



    #             # print('device = ', data_stream.TPV['device'])
    #             # print('mode = ', data_stream.TPV['mode'])
    #             # print('time = ', data_stream.TPV['time'])
    #             # print('climb = ', data_stream.TPV['climb'])
    #             # print('Longitude error estimate = ', data_stream.TPV['epx'])
    #             # print('Latitude error estimate = ', data_stream.TPV['epy'])
    #             # print('Estimated vertical error = ', data_stream.TPV['epv'])
    #             # print('speed = ', data_stream.TPV['speed'])
    #             if count == 9:
    #                 break
    # print('End')
if __name__ == '__main__':
    start = time.perf_counter()
    get_gps('fast')
    end = time.perf_counter()
    print(f"{bcolors.HEADER}GPS Fast: {end-start} sec.{bcolors.ENDC}")

    start = time.perf_counter()
    get_gps('cautious')
    end = time.perf_counter()
    print(f"{bcolors.HEADER}GPS Cautious: {end-start} sec.{bcolors.ENDC}")
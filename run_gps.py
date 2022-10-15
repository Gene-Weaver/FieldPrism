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
import time
from gps3 import gps3

gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()
for new_data in gps_socket:
    if new_data:
        data_stream.unpack(new_data)
        print('Altitude = ', data_stream.TPV['alt'])
        print('Altitude = ', data_stream.TPV['alt'])
        print('Latitude = ', data_stream.TPV['lat'])
        print('Longitude = ', data_stream.TPV['lon'])
        time.sleep(1)
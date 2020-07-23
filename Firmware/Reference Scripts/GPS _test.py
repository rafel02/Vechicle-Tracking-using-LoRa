from micropyGPS import MicropyGPS
from machine import UART
import time
# Initialize GPS
#com = UART(1,pins=('P20','P21'),  baudrate=9600) #config.TX, config.RX
com = UART(1,pins=('P12','P11'), baudrate=9600)
my_gps = MicropyGPS()

while True:
    if com.any():
        #com.writeline("helllllllllllllllooooo")
        my_sentence = com.readline()
        print('my sentence..................',my_sentence)
        for x in my_sentence:
            print('my sentence1..................',my_sentence)
            my_gps.update(chr(x))
        print('Longitud', my_gps.longitude);
        print('Latitude', my_gps.latitude);
        #    print('UTC Timestamp:', my_gps.timestamp);
        #    print('Fix Status:', my_gps.fix_stat);
        #    print('Altitude:', my_gps.altitude);
        #    print('Horizontal Dilution of Precision:', my_gps.hdop)
        #    print('Satellites in Use by Receiver:', my_gps.satellites_in_use)
        #    print('Speed in km/hour:', int(my_gps.speed[2]))
        time.sleep(5)

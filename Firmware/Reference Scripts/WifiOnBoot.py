import machine
import pycom
import time
from network import WLAN
wlan = WLAN() # get current object, without changing the mode

pycom.heartbeat(False)
print('led on')
pycom.rgbled(0x7f0000)  # red

if machine.reset_cause() != machine.SOFT_RESET:
    wlan.init(mode=WLAN.STA)
    # configuration below MUST match your home router settings!!
    #wlan.ifconfig(config=('192.168.178.10', '255.255.255.0', '192.168.178.1', '8.8.8.8'))
    #wlan.ifconfig(config=('10.0.9.80', '255.255.240.0', '10.0.0.1', '8.8.8.8'))
    wlan.ifconfig(config=('192.168.0.194', '255.255.255.0', '192.168.0.1', '8.8.8.8'))

print('STATIC IP = 192.168.0.194')

if not wlan.isconnected():
    # change the line below to match your network ssid, security and password
    #wlan.connect('TTU Campus', auth=(0, ''), timeout=5000)
    #wlan.connect('shiva', auth=(WLAN.WPA2, '9742490213'), timeout=5000)
    wlan.connect('DIR-615-JEFF', auth=(WLAN.WPA2, 'ETTU2018'), timeout=5000)
    # wlan.connect('shiva', auth=(0, '9742490213'), timeout=5000)
    print('wifi connecting')
    while not wlan.isconnected():
        machine.idle() # save power while waiting
    if wlan.isconnected():
        print('wifi connected')
wlan = WLAN()

pycom.rgbled(0x00007f) # blue
time.sleep(1)
pycom.rgbled(0x007f00) # green
print(wlan.ifconfig())
time.sleep(2)
pycom.heartbeat(True)

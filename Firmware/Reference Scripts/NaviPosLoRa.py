from micropyGPS import MicropyGPS
from machine import UART
import time
from network import LoRa
import socket
import binascii
import struct

# Initialize GPS
#com = UART(1,pins=('P20','P21'),  baudrate=9600) #config.TX, config.RX
com = UART(1,pins=('P12','P11'), baudrate=9600)
my_gps = MicropyGPS()
data=[] # 1st 4 val is of latitude and last 4 packet is longitude
dev_addrstr = '26 01 1B 6C'
nwk_swkeystr = '9E 47 98 83 D1 D7 EE 7A 93 E2 F6 85 AD 8E 13 2F'
app_swkeystr = 'FE B8 6A 5E B8 8C 46 AD C4 04 E2 AC D0 08 5E C9'

def lora_init():
	global s
	# Initialize LoRa in LORAWAN mode.
	lora = LoRa(mode=LoRa.LORAWAN)

	# create an ABP authentication params
	dev_addr = struct.unpack(">l", binascii.unhexlify(dev_addrstr.replace(' ','')))[0]
	nwk_swkey = binascii.unhexlify(nwk_swkeystr.replace(' ',''))
	app_swkey = binascii.unhexlify(app_swkeystr.replace(' ',''))

	# join a network using ABP (Activation By Personalization)
	lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

	# create a LoRa socket
	s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

	# set the LoRaWAN data rate
	s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
	print ("LORA Initialized")

def sendlorapack():
	global s
	if (s):
		s.setblocking(True)
		s.send(bytes(data))
		# make the socket non-blocking
		# (because if there's no data received it will block forever...)
		s.setblocking(False)
		rcv_data = s.recv(64)	    # get any data received (if any...)
		if (rcv_data):
			print('Received lora packet:',rcv_data)
		return 0
	else:
		print ("Error: LORA Initialized")
		return -1

def clear_data():
	list_index = len(data)-1
	while (list_index >= 0 ):
		data.pop(list_index)
		list_index = len(data)-1
	#print ('Clear data : {}'.format(data))

def set_data(la1,la2,lo1,lo2):
    if(la1<0):
        la=int( (((-1)*la1)*1000000) + ((la2/60)*1000000) )
        data.insert( 0, (0xf0 | ((la & 0x0f000000)>>24)) )
    else:
        la=int( (la1*1000000) + ((la2/60)*1000000) )
        data.insert( 0, ((la & 0x0f000000)>>24) )
    data.insert( 1,((la & 0x00ff0000)>>16) )
    data.insert( 2,((la & 0x0000ff00)>>8) )
    data.insert( 3,(la & 0x000000ff) )

    if(lo1<0):
        lo=int( (((-1)*lo1)*1000000) + ((lo2/60)*1000000) )
        data.insert(4, (0xf0 | ((lo & 0x0f000000)>>24)) )
    else:
        lo=int( (lo1*1000000) + ((lo2/60)*1000000) )
        data.insert(4, ((lo & 0x0f000000)>>24) )
    data.insert( 5,((lo & 0x00ff0000)>>16) )
    data.insert( 6,((lo & 0x0000ff00)>>8) )
    data.insert( 7,(lo & 0x000000ff) )

def get_data():
    if com.any():
        print("Got data")
        my_sentence = com.readall()
        print(my_sentence)
        for x in my_sentence:
            my_gps.update(chr(x))
        print('Longitude', my_gps.longitude);
        print('Latitude', my_gps.latitude);
        if (my_gps.latitude[0] != 0 or my_gps.longitude[0] != 0):
			set_data( my_gps.latitude[0] , my_gps.latitude[1], my_gps.longitude[0] ,my_gps.longitude[1])
        else:
			print('Invalid Packet');
			return -1
        return 0
    else:
        return -1

def test_data():
	data.insert( 0,0x02)
	data.insert( 1,0x6D)
	data.insert( 2,0xAC)
	data.insert( 3,0x07)
	data.insert( 4,0xF4)
	data.insert( 5,0x68)
	data.insert( 6,0xFC)
	data.insert( 7,0xBC)
	return 0

lora_init()
while 1:
	count = 0
	if( get_data() != -1):
		print('Data Pack : {}'.format(data));
		if( sendlorapack() != -1):
			print('Packet Sent');
		else:
			print('Failed to send packet');
			lora_init()
	else:
		print("No data");

	clear_data()					#clearing buffer for next cycle.
	print("\n")
	time.sleep(20)

from network import LoRa
import socket
import binascii
import struct
from machine import UART
import time

data = []
uart_baud = 19200
uart = UART(1, uart_baud)
open_cmd = 'O'
close_cmd = 'C'
dist_cmd = 'D'
tem_pwr_cmd = 'S'
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

lora_init()
while 1:
	count = 0
	data.insert( 0,(21 >> 8)  )
	data.insert( 1,(35 & 0xFF))
	print('Data Pack : {}'.format(data))
	if( -1 != sendlorapack() ):
		print('packet send pass');
	else:
		print('packet send failed');
		lora_init()
	clear_data()					#clearing buffer for next cycle.
	print("\n")
	time.sleep(30)

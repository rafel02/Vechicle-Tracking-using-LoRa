from network import LoRa
import socket
import binascii
import struct
from machine import UART
import time

data = [21 32]
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

def uart_init():
	uart.init(uart_baud, bits=8, parity=None, stop=1) # init with given parameters
	time.sleep(2)
	print ("UART Initialized")

def clear_data():
	list_index = len(data)-1
	while (list_index >= 0 ):
		data.pop(list_index)
		list_index = len(data)-1
	#print ('Clear data : {}'.format(data))

def set_distance(rsp_str):
	dis_rsp ='D:';
	#sp_str = 'D: 22.332m, 1480'	#for testing

	base = int(rsp_str.find(dis_rsp))
	try:
		if(rsp_str[base+8] == 'm'):
			dist = float(rsp_str[base+3:base+8])
		else:
			dist = float(rsp_str[base+3:base+9])
		print ('Distance : {} m'.format(dist))
		dist = int( dist *1000)
		data.insert( 0,(dist >> 8)  )
		data.insert( 1,(dist & 0xFF))
		return 0
	except Exception as ValueError:
		print ("Error: Invalid response")
		return -1

#def set_temppwr(rsp_str)

def readdata(exp_rsp):							# Read response at UART
	if uart.any():
		uart_buff = str(uart.readall())
		print ('Response packet : {}'.format(uart_buff))
		if uart_buff.find(exp_rsp) >= 0:
			#print ("Response match")
			return uart_buff
			#return 'D: 11.223dd'
		else:
			print ("Response formate incorrect")
			return -1
	else:
		print ("No response")
		return -1

def cmd_rsp(cmd, exp_rsp):						# Send command on UART
	#print (cmd)
	uart.write(cmd)
	time.sleep(3)
	rsp = readdata(exp_rsp)
	time.sleep(2)
	if -1 != rsp:
		return rsp
	else:
		return -1;

while 1:
	count = 0
	lora_init()
	uart_init()
	while (-1 == cmd_rsp(open_cmd ,'O,OK') and count < 3):
		print ("Error: Fail to open UART, Retrying")
		time.sleep(2)
		count +=1

	if (count < 3):
		print ('UART Opened')

	while (count <3):
		rsp = cmd_rsp(dist_cmd,'D:')
		if (-1 != rsp):
			if( -1 != set_distance(rsp) ):
				rsp = cmd_rsp(tem_pwr_cmd ,'S:')
				if (-1 != rsp):
					print('Data Pack : {}'.format(data))
					if( -1 != sendlorapack() ):
						count =0
					else:
						count+=1
						lora_init()
				else:
					count +=1
			else:
				count +=1
		clear_data()					#clearing buffer for next cycle.
		print("\n")
		time.sleep(30)

	count=0
	while (-1 == cmd_rsp(close_cmd ,'C,OK') and count < 3):
		time.sleep(2)
		print ("Fail to close UART, Restrying")
		count +=1

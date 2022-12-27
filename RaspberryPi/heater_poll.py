import crcmod.predefined
import serial
from time import sleep
import crcmod
import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions

def finishMessage(byteList):
	newPacket = bytearray()
	newPacket.append(0x72)

	for bit in byteList:
		newPacket.append(bit)

	crcfunc = crcmod.predefined.mkCrcFun('modbus')

	crc = crcfunc(byteList)

	val = bytes([crc >> 8 % 256,crc % 256])

	for bit in val:
		newPacket.append(bit)

	return newPacket


def rxMessage(client, userdata, msg):
	global heater_mode_val, heater_temp_val, ventilation_val, power_level_val
	print(f"Message received [{msg.topic}]: {msg.payload}")
	#print(client)
	#print(userdata)
	if(msg.topic == "van/diesel/control"):
		if(msg.payload == b'On'):
			print("Sending heat command")
			powerOn(heater_mode_val, heater_temp_val, ventilation_val, power_level_val)
		if(msg.payload == b'Off'):
			print("Sending off command")
			ser.write('F'.encode())

	if(msg.topic == "van/diesel/setpoint_heater_temp"):
		heater_temp_val = int(msg.payload)
		print(heater_temp_val)
		send_command(heater_mode_val, heater_temp_val, ventilation_val, power_level_val)

	if(msg.topic == "van/diesel/setpoint_power_level"):
		power_level_val = int(msg.payload)
		print(power_level_val)
		send_command(heater_mode_val, heater_temp_val, ventilation_val, power_level_val)

	if(msg.topic == "van/diesel/setpoint_heater_mode_string"):
		if(msg.payload == b'Power'):
			heater_mode_val = 4
		if(msg.payload == b'Panel'):
			heater_mode_val = 2
		if(msg.payload == b'Heater'):
			heater_mode_val = 1
				
		print(heater_mode_val)
		send_command(heater_mode_val, heater_temp_val, ventilation_val, power_level_val)

	if(msg.topic == "van/diesel/setpoint_ventilation"):
		ventilation_val = int(msg.payload)
		print(ventilation_val)
		send_command(heater_mode_val, heater_temp_val, ventilation_val, power_level_val)


def parse_and_submit(serial_data, ident_string, index, topic):
	lines = str(serial_data)
	find_index = lines.find(ident_string)
	if(find_index > -1):
		#found the string in the data
		serial_slice = lines[find_index:]
		#move the found data to a slice
		hex_data = serial_slice.split(" ")
		if(len(hex_data) > (index + 1)):
			#not teh last element so not split data
			data = hex_data[index]
			if(len(data) < 5): #0x0 0x00 0xFFFF0 0xFFFF00
				data = data[2:]
			else:
				data = data[8:]

			try:
				value = int(data, 16)
				client.publish(topic, value)
				return value
			except:
				client.publish(topic+"_debug", "parse_error" + data)



def send_command(mode, temp, vent, powe):
	packet = bytearray()
	packet.append(0xAA) #start
	packet.append(0x03) #from controller
	packet.append(0x06) #6 bytes in message
	packet.append(0x00) #blank
	packet.append(0x02) #get/set command
	packet.append(0xFF) #unused
	packet.append(0xFF) #unused
	packet.append(mode)
	packet.append(temp)
	packet.append(vent)
	packet.append(powe)

	message = finishMessage(packet)
	
	for bit in message:
		print(hex(bit))

	for i in range(2):
		ser.write(message)
		sleep(0.4)		
		ser.flushInput()

		
def powerOn(mode, temp, vent, powe):
	packet = bytearray()
	packet.append(0xAA)
	packet.append(0x03)
	packet.append(0x06)
	packet.append(0x00)
	packet.append(0x01) #turn on
	packet.append(0xFF)
	packet.append(0xFF)
	packet.append(mode)
	packet.append(temp)
	packet.append(vent)
	packet.append(powe)

	message = finishMessage(packet)
	
	for bit in message:
		print(hex(bit))

	for i in range(2):
		ser.write(message)
		sleep(0.4)		
		ser.flushInput()




mqtt_broker = ""
mqtt_port = 1
mqtt_user = ""
mqtt_pswr = ""


client = mqtt.Client("VAN-DIESEL", protocol=5)
client.username_pw_set(mqtt_user, mqtt_pswr)
client.connect(mqtt_broker, mqtt_port)

client.on_message = rxMessage


options = SubscribeOptions(qos = 1, noLocal = True)

client.subscribe("van/diesel/control")
client.subscribe("van/diesel/setpoint_power_level", options=options)
client.subscribe("van/diesel/setpoint_heater_temp", options=options)
client.subscribe("van/diesel/setpoint_ventilation", options=options)
client.subscribe("van/diesel/setpoint_heater_mode_string", options=options)

heater_temp_cont = "C >> 0XFFFFFFAA 0X3 0X1 0X0 0X11 0X" #for some reason FFFF's are added to messages? needs fixing
heater_temp_cont_idx = 7

heater_temp_heat = "H >> 0XFFFFFFAA 0X4 0X1 0X0 0X11 0X"
heater_temp_heat_idx = 7

heater_state_string = "H >> 0XFFFFFFAA 0X4 0X13 0X0 0XF"
heater_state_index  = 16

heater_voltage_string = heater_state_string
heater_voltage_index  = 13

heater_coretemp_string = heater_state_string
heater_coretemp_index  = 15

heater_fanspd_string = heater_state_string
heater_fanspd_index  = 18

heater_fanspd2_string = heater_state_string
heater_fanspd2_index  = 19

heater_fuel_string = heater_state_string
heater_fuel_index  = 21

heater_fuel2_string = heater_state_string
heater_fuel2_index  = 23

heater_glow_string = heater_state_string
heater_glow_index  = 24


setpoint_string = "H >> 0XFFFFFFAA 0X4 0X6 0X0 0X"
heater_mode  = 9
heater_temp  = 10
ventilation  = 11
power_level  = 12
unknown      = 8
unknown2      = 7

heater_mode_val = -1
heater_temp_val = -1
ventilation_val = -1
power_level_val = -1



def checkTemperature():
	global heater_mode_val, heater_temp_val, ventilation_val, power_level_val
	serial_collect = ser.read(ser.inWaiting())

	parse_and_submit(serial_collect, heater_temp_cont, heater_temp_cont_idx, "van/diesel/temperature_controller")
	parse_and_submit(serial_collect, heater_temp_heat, heater_temp_heat_idx, "van/diesel/temperature_heater")

	parse_and_submit(serial_collect, heater_state_string, heater_state_index, "van/diesel/heater_state_n")

	parse_and_submit(serial_collect, heater_voltage_string, heater_voltage_index, "van/diesel/heater_voltage")
	parse_and_submit(serial_collect, heater_coretemp_string, heater_coretemp_index, "van/diesel/heater_coretemp")
	parse_and_submit(serial_collect, heater_fanspd_string, heater_fanspd_index, "van/diesel/heater_fanspd")
	parse_and_submit(serial_collect, heater_fanspd2_string, heater_fanspd2_index, "van/diesel/heater_fanspd2")
	parse_and_submit(serial_collect, heater_fuel_string, heater_fuel_index, "van/diesel/heater_fuel")
	parse_and_submit(serial_collect, heater_fuel2_string, heater_fuel2_index, "van/diesel/heater_fuel2")
	parse_and_submit(serial_collect, heater_glow_string, heater_glow_index, "van/diesel/heater_glow")

	heater_mode_val = parse_and_submit(serial_collect, setpoint_string, heater_mode, "van/diesel/setpoint_heater_mode")
	if(heater_mode_val) == 1:
		client.publish("van/diesel/setpoint_heater_mode_string", "Heater")
	if(heater_mode_val) == 2:
		client.publish("van/diesel/setpoint_heater_mode_string", "Panel")
	if(heater_mode_val) == 4:
		client.publish("van/diesel/setpoint_heater_mode_string", "Power")
		
	heater_temp_val = parse_and_submit(serial_collect, setpoint_string, heater_temp, "van/diesel/setpoint_heater_temp")
	ventilation_val = parse_and_submit(serial_collect, setpoint_string, ventilation, "van/diesel/setpoint_ventilation")
	power_level_val = parse_and_submit(serial_collect, setpoint_string, power_level, "van/diesel/setpoint_power_level")
	parse_and_submit(serial_collect, setpoint_string, unknown, "van/diesel/setpoint_unknown")
	parse_and_submit(serial_collect, setpoint_string, unknown2, "van/diesel/setpoint_unknown2")

	line = str(serial_collect)
	if(line.find(heater_state_string) > -1):
		#print("Heater State")
		data = line[line.find(heater_state_string):]
		if(len(data) > 130):
							bytes = data.split(" ")
							temp = bytes[heater_state_index]
							temp = temp[2:]
							temp = int(temp, 16)
							#print(temp)
							if temp == 0:
									client.publish("van/diesel/heater_state", "off")
									client.publish("van/diesel/heater_state_simple", "OFF")
							if temp == 1:
									client.publish("van/diesel/heater_state", "starting")
									client.publish("van/diesel/heater_state_simple", "ON")
							if temp == 4:
									client.publish("van/diesel/heater_state", "heating")
									client.publish("van/diesel/heater_state_simple", "ON")
							if temp == 5:
									client.publish("van/diesel/heater_state", "clearing-shutting-down")
									client.publish("van/diesel/heater_state_simple", "OFF")
							if temp == 6:
									client.publish("van/diesel/heater_state", "heating-idle")		
									client.publish("van/diesel/heater_state_simple", "ON")		

ser = serial.Serial("/dev/ttyUSB0", 115200)

while 1:
	if(ser.inWaiting() > 500):
		checkTemperature()

	client.loop()



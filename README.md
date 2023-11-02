# AutothermDieselRepeater
A set of scripts to integrate autotherm diesel heater into home assistant through MQTT.

This results in a live and updated controller for HA that is able change all settings available through the (PU-27) controller. The controller polls for settings so changes on HA will reflect in the controller and vice versa allowing for a seamless integration.

Example lovelace card is included which results in:

![lovelace card](https://github.com/csreades/AutothermDieselRepeater/blob/main/assets/lovelace_card_control.png)

The card requires three helpers to be created to work correctly. Screenshots of these are in the HA folder.

The integration has three elements:

	Control Panel
	     |
	Arduino Mega    -   Raspberry Pi   -   MQTT     - HA
        |
	   Heater




 - Arduino Mega 2560
![Arduino2560](https://github.com/csreades/AutothermDieselRepeater/blob/main/assets/arduinomega2560.webp)
 - Raspberry Pi (acting as a wifi-mqtt bridge)
 - MQTT and HA server
 
The arduino sketch is included in "ArduinoMega", the arduino Mega was selected as it has three hardware serial ports and runs on 5V logic. It is placed inbetween the heater and the control panel so that it can listen and repeat all traffic to the Pi but also inject commands. The sketch only has the shutdown command inbuilt and the rest of the commands are created by the Pi. Currently there seems to be a bug in this code that inserts extra "FFFF"s in the traffic.
 
The python file running on the Pi is in "RaspberryPi". It translates the repeated data to variables and posts them to MQTT. It also subscribes to certain control and if there is a published change it creates the command and sends it to the arduino for insertion.
 
The final scripts are in "HomeAssistant" and are excerpts from my HA in how I have integrated this specific system.
 
Finally there are the STL files for a mount for the mega so it can be mounted.
 
For wiring:

	Controller
		Red		- Heater-Red
		Blue		- Arduino GND
		Green (RX)	- Arduino 18 (TX)
		White (TX)	- Arduino 19 (RX)

	Heater
		Red		- Heater-Red
		Blue		- Arduino GND
		Green (TX)	- Arduino 17 (RX)
		White (RX)	- Arduino 16 (TX)

	

Credit for help in integration comes from:

https://grimoire314.wordpress.com/2018/08/22/planar-diesel-heater-controller-reverse-engineering/
https://grimoire314.wordpress.com/2019/03/21/autoterm-planar-diesel-heater-controller-reverse-engineering-part-2/
http://schlussdienst.net/html/planar-2d-protocol.md


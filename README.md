# AutothermDieselRepeater
A set of scripts to integrate autotherm diesel heater into home assistant through MQTT.

This results in a live and updated controller for HA that is able change all settings available through the (PU-27) controller. The controller polls for settings so changes on HA will reflect in the controller and vice versa allowing for a seamless integration.

Example lovelace card is included which results in:

![alt text](https://github.com/csreades/AutothermDieselRepeater/blob/main/assets/lovelace_card_control.png)
import serial
import time
import paho.mqtt.client as mqtt
import re
import datetime
import json
import argparse 
import os


#distance from sensor to water min level
zero_level = 131 

# FIR Class to average
class Fir(object):
    def __init__(self, length):
        self.fir = []
        self.cnt = 0
        self.length = length
        for _ in range(self.length):
            self.fir.append(0)
     
    def put(self, data):
        self.fir[self.cnt] = data
        if self.cnt == (self.length-1):
            self.cnt = 0
        else:
            self.cnt += 1
     
    def average(self):
        avr = 0
        for i in self.fir:
            avr += i
        return avr/self.length    

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Well depth sensors processing.')
    parser.add_argument('mqtt_broker_addr', type=str, nargs=1, help='MQTT Broker server name')
    args = parser.parse_args()
    mqtt_server = args.mqtt_broker_addr[0]

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(mqtt_server, 1883, 60)
    client.loop_start()

    ser = serial.Serial('/dev/ttyUSB0',115200, timeout=20)

    fir = Fir(100)

    while True:
     line = ser.readline()
     searchObj = re.search( b'distance: ([0-9]+) ', line, re.M|re.I)
     if searchObj:
         depth = zero_level - int(searchObj.group(1))/58.0
         fir.put(depth)
         avr = fir.average()
         message = '{{"depth": {0:3.1f}}}'.format(depth)
         print(message, "{0:3.1f}".format(avr))
         client.publish("sensor.well_status",message)







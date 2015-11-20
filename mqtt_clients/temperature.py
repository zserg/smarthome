import serial
import time
import paho.mqtt.client as mqtt
import re
import datetime
import json
import sys
import argparse 

#b'\r28:FF:9A:58:6F:14:04:CA: - Temp: 0x00AB (0010 C);\n'

dSensors = {'28:AA:80:DE:01:00:00:F9':'sensor_vault_top',
            '28:FF:9A:58:6F:14:04:CA':'sensor_vault_bot'}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def parse_sensor(line):
    rule = b'([0-9ABCDEF:]+): - Temp: ([0-9xABCDEF]+) \(([0-9]+) C\)'
    searchObj = re.search(rule, line, re.M|re.I)
    if searchObj:
        sensorId = (searchObj.group(1)).decode('ascii')
        sensorRaw = int(searchObj.group(2),16)
        if sensorRaw > 0x7fff:
          sensorRaw -= 0x10000
        sensorTemp = int(searchObj.group(3))
        return sensorId, sensorRaw, sensorTemp
    else:
        return 'error',0,0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Temperature sensors processing.')
    parser.add_argument('mqtt_broker_addr', type=str, nargs=1, help='MQTT Broker server name')
    args = parser.parse_args()
    mqtt_server = args.mqtt_broker_addr[0]
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_server, 1883, 60)
    client.loop_start()

    ser = serial.Serial('/dev/ttyUSB1',38400, timeout=20)

    while True:
         line = ser.readline()
         (senId,senRaw,senTemp) = parse_sensor(line)
         if senId in dSensors: 
              message = '{{"sensor_id": "{0}","raw_data": {1:6d}, \
                           "temperature": {2:4d}}}'.format(
                           senId, senRaw, senTemp)
              print(message)
              client.publish("sensor.vault_status",message)
              #print(dSensors[senId])
              #print(senTemp)
              client.publish("{0}.temperature".format(dSensors[senId]),senTemp)







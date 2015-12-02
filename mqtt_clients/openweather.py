"""
http://api.openweathermap.org/data/2.5/weather?q=Daugavpils&appid=b6ea72690d28e65f1c5c441232236df8
"""

import urllib.request
import json
import paho.mqtt.client as mqtt
import time
import argparse


appid = 'b6ea72690d28e65f1c5c441232236df8'
#city = 'Daugavpils'
city = 'Visaginas'
uri = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city,appid)


def get_temp(uri):
    req = urllib.request.Request(uri)
    try: 
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)
        return None
    else:
      
        resp = response.read()
        print(resp)
        weather_data = resp.decode('ascii')
        try:
           return int((json.loads(weather_data))['main']['temp'] - 273.15)
        except KeyError:
            print("KeyError")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def mqtt_init(mqtt_server, mqtt_port):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(mqtt_server, mqtt_port, 60)
    client.loop_start()
    return client


def put_mqtt(client,temperature):
    message = '{{"sensor_id": "{0}", "temperature": {1:4d}}}'.format('openweathermap', temperature)
    print(message)
    client.publish("sensor.vault_status",message)
    client.publish("sensor_country_house_outdoor.temperature",temperature)


if __name__ == "__main__":    
     parser = argparse.ArgumentParser(description='Well depth sensors processing.')
     parser.add_argument('mqtt_broker_addr', type=str, nargs=1, help='MQTT Broker server name')
     args = parser.parse_args()
     mqtt_server = args.mqtt_broker_addr[0]
     mqtt_port = 1883
     mqtt_client = mqtt_init(mqtt_server, mqtt_port)
     while(1):
         temperature = get_temp(uri)
         print(temperature)
         if temperature is not None:
             put_mqtt(mqtt_client,temperature)
             time.sleep(30)






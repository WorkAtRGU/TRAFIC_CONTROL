import paho.mqtt.client as mqtt
import re
import time
import ssl
from sense_hat import SenseHat

sense=SenseHat()

broker="node02.myqtthub.com"
broker_port=8883
client_id="Raspberry2MainRoad2"
user_name="asri84368"
password="1YRdhAnN-MfoxC9Yt"

green=(0,255,0) #turn green
red=(255,0,0) #turn red

def on_connect(client, userdata, flags, rc):
    sense.clear()
    client.subscribe("hub-asri84368/mainRoad2")
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+string.payload)
    if msg.payload == "{'light':'red'}":
            sense.clear((red))
    if msg.payload=="{'light':'green'}":
            sense.clear((green))

client=mqtt.Client()
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker,broker_port,60)
client.loop(1)

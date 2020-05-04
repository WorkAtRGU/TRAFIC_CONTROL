#!/usr/bin/python

import paho.mqtt.client as mqtt
import time
import ssl
import json
from sense_hat import SenseHat

host          = "node02.myqtthub.com"
port          = 8883
clean_session = True
client_id     = "Raspberry2MainRoad2"
user_name     = "asri84368"
password      = "1YRdhAnN-MfoxC9Yt"

sense=SenseHat()

#Setting up traffic light colors
green=(0,255,0) 
red=(255,0,0)

#to handle not new messages store the time of the latest
latestMessageTime = time.time()

#Parse and react to message
def on_message(client, userdata, msg):
    
    jsonStr = str(msg.payload.decode("UTF-8"))
    
    #parse the JSON control data
    control = json.loads(jsonStr)
    junction = control["featureOfInterest"]
    publishTime = control["publishTime"]
    status = control["status"]

    #Print all messages recieved
    print(str(control))

    #If control data is for this junction and the message is new, react
    if str(junction) == "Junction One" and publishTime > latestMessageTime and str(status) == "active":   

        #Store the publish time as latest message time
        global latestMessageTime
        latestMessageTime = publishTime
        result = control["hasResult"]
        color = result["value"]

        #If control data is red, turn LED red
        if str(color) == "red":
            sense.clear((red))

        #Else turn LED green
        else:
            sense.clear((green))

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print ("Connect %s result is: %s" % (host, rc))

    if rc == 0:
        client.connected_flag = True
        print ("connected OK")

        #Subscribing every on connect
        client.subscribe("hub-asri84368/mainRoad2")
        return
    
    print ("Failed to connect to %s, error was, rc=%s" % rc)
    sys.exit (-1)

# Define clientId, host, user and password
client = mqtt.Client (client_id = client_id, clean_session = clean_session)
client.username_pw_set (user_name, password)

client.on_connect = on_connect
client.on_message = on_message

#configure TLS connection
client.tls_set (cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set (False)
port = 8883

# connect using standard unsecure MQTT with keepalive to 60
client.connect (host, port, keepalive = 60)
client.loop_start()

client.connected_flag = False
while not client.connected_flag:           #wait in loop
    client.loop()
    time.sleep (1)

#Clearing senseHat first
sense.clear()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()
    print("Connection closed.")


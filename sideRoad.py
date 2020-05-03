#!/usr/bin/python

import paho.mqtt.client as mqtt
import re
import time
import ssl
import json
from sense_hat import SenseHat

host          = "node02.myqtthub.com"
port          = 8883
clean_session = True
client_id     = "raspberry3sideroad"
user_name     = "asri84368"
password      = "1YRdhAnN-MfoxC9Yt"

sense=SenseHat()

#Setting up traffic light colors
green=(0,255,0) 
red=(255,0,0) 

#Parse and react to message
def on_message(client, userdata, msg):
    
    jsonStr = str(msg.payload.decode("UTF-8"))

    #parse the JSON control data
    control = json.loads(jsonStr)
    print(str(control))
    junction = control["featureOfInterest"]

    #If control data is for this junction, react
    if str(junction) == "Junction One":   
        result = control["hasResult"]
        print(str(result))
        color = result["value"]
        print(str(color))
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
        return
    
    print ("Failed to connect to %s, error was, rc=%s" % rc)
    # handle error here
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


sense.clear()
client.subscribe("hub-asri84368/sideRoad")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()

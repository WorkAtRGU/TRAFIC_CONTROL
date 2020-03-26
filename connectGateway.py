#!/usr/bin/python

import paho.mqtt.client as mqtt
import time
import ssl

host          = "node02.myqtthub.com"
port          = 8883
clean_session = True
client_id     = "GatewayRPI"
user_name     = "asri84368"
password      = "1YRdhAnN-MfoxC9Yt"

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print ("Connect %s result is: %s" % (host, rc))
    
    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.
    client.subscribe("hub-asri84368/sideRoad")
    client.subscribe("hub-asri84368/mainRoad1")
    client.subscribe("hub-asri84368/mainRoad2")
    client.subscribe("hub-asri84368/isSpace")

    if rc == 0:
        client.connected_flag = True
        print ("connected OK")
        return
    
    print ("Failed to connect to %s, error was, rc=%s" % rc)
    # handle error here
    sys.exit (-1)


def on_message(client, userdata, msg):
    """ Callback called for every PUBLISH received """
    print ("%s => %s" % (msg.topi, str(msg.payload)))

# Define clientId, host, user and password
client = mqtt.Client (client_id = client_id, clean_session = clean_session)
client.username_pw_set (user_name, password)

client.on_connect = on_connect
client.on_message = on_message

# configure TLS connection
client.tls_set (cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set (False)
port = 8883

# connect using standard unsecure MQTT with keepalive to 60
client.connect (host, port, keepalive = 60)
client.connected_flag = False
while not client.connected_flag:           #wait in loop
    client.loop()
    time.sleep (1)

# publish message (optionally configuring qos=1, qos=2 and retain=True/False)
ret = client.publish ("hub-asri84368/mainRoad1", "green")
print ("MainRoad1 set to green with ret=%s" % ret)
ret = client.publish ("hub-asri84368/mainRoad2", "green")
print ("MainRoad2 set to green with ret=%s" % ret)
ret = client.publish ("hub-asri84368/sideRoad", "red")
print ("SideRoad set to red with ret=%s" % ret)

sideRoad = input("Please enter the side road value True/False\n")
isSpace = input("Please enter the space value True/False\n")

while sideRoad != "exit":
    if sideRoad=="True":
        while isSpace != "True":
            isSpace = input("Please enter the space value True/False\n")

        while sideRoad=="True":
            while isSpace=="True":
                mainRoad1 = input("Please enter the main road 1 road value True/False\n")
                if mainRoad1 == "True":
                    ret = client.publish ("hub-asri84368/mainRoad1", "red")
                    print ("MainRoad1 set to red with ret=%s" % ret)

                mainRoad2 = input("Please enter the main road 2 True/False\n")
                if mainRoad2 == "True":
                    ret = client.publish ("hub-asri84368/mainRoad1", "red")
                    print ("MainRoad2 set to red with ret=%s" % ret)
                    
                ret = client.publish ("hub-asri84368/sideRoad", "green")
                print ("SideRoad set to green with ret=%s" % ret)
                
                isSpace = input("Please enter the space value True/False\n")
                
            isSpace = input("Please enter the space value True/False\n")
            sideRoad = input("Please enter the side road value True/False\n")

    else:
        ret = client.publish ("hub-asri84368/mainRoad1", "green")
        print ("MainRoad1 set to green with ret=%s" % ret)
        ret = client.publish ("hub-asri84368/mainRoad2", "green")
        print ("MainRoad2 set to green with ret=%s" % ret)
        ret = client.publish ("hub-asri84368/sideRoad", "red")
        print ("SideRoad set to red with ret=%s" % ret)        
        
    client.loop ()
    sideRoad = input("Please enter the side road value True/False\n")
    isSpace = input("Please enter the space value True/False\n") 
    

# close connection
client.disconnect ()

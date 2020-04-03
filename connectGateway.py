#!/usr/bin/python

import paho.mqtt.client as mqtt
import time
import ssl
from sense_hat import SenseHat

sense = SenseHat()

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

#sensor variables
sideRoad = False;
isSpace = False;
mainRoad1 = False;
mainRoad2 = False;

#variables for monitoring frequency of the queue becoming long over 2 mins
numOfSideRoadTrue = 0;
s_road_max_time = 120;
s_road_start_time = 0;

#variables to time limit adapted system behavior
mod_max_time = 60;
mod_start_time = 0;

def getJoystickDirection():
    while True: #waiting for min one released event
           event = sense.stick.wait_for_event(emptybuffer=True)
           if event.action != "released": #necessary to ignore pressed event action
               break
    print(event)
    print(event.direction)
    return event.direction

def setSideRoad():
    print("Please indicate side road value using joystick, True:move right then press, False: move to any direction but right then press\n")
    global sideRoad
    sideRoad = (getJoystickDirection() == "right")
    print("The value you indicated is" + str(sideRoad))
    
def setIsSpace():
    print("Please enter the space value\n")
    global isSpace
    isSpace = getJoystickDirection() == "right"
    global s_road_start_time
    global s_road_max_time
    if isSpace ==True:
        if (time.time()-s_road_start_time)<s_road_max_time:
            numOfSideRoadTrue+=1;
        else:
            numOfSideRoadTrue=0;
    print("The value you indicated is" + str(isSpace))
    if numOfSideRoadTrue<10:
        while time.time()-mod_start_time<mod_max_time:
            modified_behavior()

#adapted behavior keeps side road lamps green for 1 min no matter the side road sensor
def modified_behavior():
    while isSpace == True:
        check_main_road()
        setIsSpace()
            
def setMainRoad1():
    print("Please indicate main road 1 value\n")
    global mainRoad1
    mainRoad1 = getJoystickDirection() == "right"
    print("The value you indicated is" + str(mainRoad1))
    
def setMainRoad2():
    print("Please indicate main road 2 value\n")
    global mainRoad2
    mainRoad2 = getJoystickDirection() == "right"
    print("The value you indicated is" + str(mainRoad2))

def check_main_road():
    setMainRoad1()
    if mainRoad1 == True:
        ret = client.publish ("hub-asri84368/mainRoad1", "red")
        print ("MainRoad1 set to red")
    setMainRoad2()
    if mainRoad2 == True:
        ret = client.publish ("hub-asri84368/mainRoad1", "red")
        print ("MainRoad2 set to red")
    ret = client.publish ("hub-asri84368/sideRoad", "green")
    print ("SideRoad set to green")

def reset():
    ret = client.publish ("hub-asri84368/mainRoad1", "green")
    print ("MainRoad1 set to green")
    ret = client.publish ("hub-asri84368/mainRoad2", "green")
    print ("MainRoad2 set to green")
    ret = client.publish ("hub-asri84368/sideRoad", "red")
    print ("SideRoad set to red")
    
#initialise lamps    
reset()

#initialise variables
setSideRoad()
setIsSpace()
s_road_start_time = time.time()

while True:
    if sideRoad == True:
        while isSpace != True:
            setIsSpace()
        while sideRoad == True:           
            while isSpace == True:
                check_main_road()
                setIsSpace()
                setSideRoad()
                if sideRoad == False:
                    break;
            setIsSpace()
            setSideRoad()
    else:
        reset()             
    setSideRoad()
    setIsSpace()
    client.loop()
    

# close connection
client.disconnect ()

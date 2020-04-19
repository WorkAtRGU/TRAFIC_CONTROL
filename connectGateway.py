#!/usr/bin/python
try:
    import paho.mqtt.client as mqtt
    import time
    import ssl
    import sys
    from sense_hat import SenseHat
except ImportError:
    print("There was an import error, please check.")

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

    if rc == 0:
        client.connected_flag = True
        print ("connected OK")
        return
    #in case of error print error value and exit
    print ("Failed to connect to %s, error was, rc=%s" % rc)
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

client.loop_start()

client.connected_flag = False
while not client.connected_flag:           #wait in loop
    client.loop()
    time.sleep (1)

#sensor variables
sideRoad = False;
isSpace = False;
mainRoad1 = False;
mainRoad2 = False;

#variables for monitoring frequency of the queue becoming long over 1 min
numOfSideRoadTrue = 0;
s_road_max_time = 60;
s_road_start_time = time.time();

#variables to time limit adapted system behavior
mod_max_time = 30;
mod_start_time = time.time();

#function to wait for joystick event and capture and return the direction of the released event
def getJoystickDirection():
        #waiting for minimum one released event
        while True:
            #emptyBuffer=True is used to get rid of events generated before waiting starts
            event = sense.stick.wait_for_event(emptybuffer=True)
            #necessary to ignore pressed or released event action not to duplicate trigerred actions
            if event.action != "released": 
                break
        return event.direction

#function to set the sideRoad variable, record the # of True values, initiate modified behavior if treshhold is exceeded
def setSideRoad():
    print("Please indicate side road value using joystick, right=True, anything else=False\n")
    global sideRoad
    sideRoad = (getJoystickDirection() == "right")
    global s_road_start_time
    global s_road_max_time
    global numOfSideRoadTrue
    if isSpace == True:
        if time.time() - s_road_start_time < s_road_max_time:
            numOfSideRoadTrue += 1;
        else:
            numOfSideRoadTrue = 0;
            s_road_start_time = time.time()
    print("The value you indicated is " + str(sideRoad) + "\n")
    if numOfSideRoadTrue >= 1:
        #tells the user that modified behavior started
        print("Modified behavior started.\n")
        while time.time() - mod_start_time < mod_max_time:
            modified_behavior()

#adapted behavior keeps side road lamps green for 1 min no matter the side road sensor
def modified_behavior():
    global mod_start_time
    global mod_max_time
    while  time.time() - s_road_start_time < s_road_max_time:
        setIsSpace()
        if isSpace == True:
            check_main_road()
        else:
            reset()
    print("Modified behavior stops.\n")

#function to set the isSpace variable  
def setIsSpace():
    print("Please indicate the space value using the joystick right=True, anything else:false\n")
    global isSpace
    isSpace = getJoystickDirection() == "right"
    print("The value you indicated is " + str(isSpace) + "\n")
    
#functions to set mainRoad1 and mainRoad2 variables
def setMainRoad1():
    print("Please indicate main road 1 value\n")
    global mainRoad1
    mainRoad1 = getJoystickDirection() == "right"
    print("The value you indicated is " + str(mainRoad1) + "\n")
    
def setMainRoad2():
    print("Please indicate main road 2 value\n")
    global mainRoad2
    mainRoad2 = getJoystickDirection() == "right"
    print("The value you indicated is " + str(mainRoad2) + "\n")

#function to publish data according to user input
def check_main_road():
    setMainRoad1()
    if mainRoad1 == True:
        ret = client.publish ("hub-asri84368/mainRoad1", "{'light':'red'}")
        print ("MainRoad1 set to red.\n")
    setMainRoad2()
    if mainRoad2 == True:
        ret = client.publish ("hub-asri84368/mainRoad1", "{'light':'red'}")
        print ("MainRoad2 set to red\n")
    ret = client.publish ("hub-asri84368/sideRoad", "{'light':'green'}")
    print ("SideRoad set to green.\n")

#function to reset all lamps, main roads to green, side road to red
def reset():
    ret = client.publish ("hub-asri84368/mainRoad1", "{'light':'green'}")
    print ("MainRoad1 set to green.\n")
    ret = client.publish ("hub-asri84368/mainRoad2", "{'light':'green'}")
    print ("MainRoad2 set to green.\n")
    ret = client.publish ("hub-asri84368/sideRoad", "{'light':'red'}")
    print ("SideRoad set to red.\n")
    
#initialise lamps with reset()    
reset()

#initialise variables for while cycles and time restriction on side road value recording
setSideRoad()
setIsSpace()
s_road_start_time = time.time()

try:
    while True:
        if sideRoad == True:
            if isSpace == True:
                check_main_road()
        else:
            reset()
        setSideRoad()
        setIsSpace()

#Press Ctrl+C to generate a KeyboardInterrupt. Please press too joystick to exit
except KeyboardInterrupt:
    print("Simulation exited. Connection is about to be closed.\n")
    client.disconnect()
    client.loop_stop()
    sys.exit(0)

    



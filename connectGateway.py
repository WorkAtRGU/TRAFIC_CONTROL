#!/usr/bin/python
try:
    import paho.mqtt.client as mqtt
    import time
    import ssl
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
    
    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.
##    client.subscribe("hub-asri84368/sideRoad")
##    client.subscribe("hub-asri84368/mainRoad1")
##    client.subscribe("hub-asri84368/mainRoad2")
##    client.subscribe("hub-asri84368/isSpace")

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
mod_max_time = 10;
mod_start_time = 0;

def getJoystickDirection():
        while True: #waiting for min one released event
               event = sense.stick.wait_for_event(emptybuffer=True)
               if event.action != "released": #necessary to ignore pressed event action
                   break
        return event.direction

def setSideRoad():
    print("Please indicate side road value using joystick, right=True, anything else=False\n")
    global sideRoad
    sideRoad = (getJoystickDirection() == "right")
    global s_road_start_time
    global s_road_max_time
    global numOfSideRoadTrue
    if isSpace ==True:
        if (time.time()-s_road_start_time)<s_road_max_time:
            numOfSideRoadTrue+=1;
        else:
            numOfSideRoadTrue=0;
    print("The value you indicated is " + str(sideRoad) + "\n")
    if numOfSideRoadTrue>=2:
        while time.time()-mod_start_time<mod_max_time:
            modified_behavior()
    
def setIsSpace():
    print("Please indicate the space value using the joystick right=True, anything else:false\n")
    global isSpace
    isSpace = getJoystickDirection() == "right"
    print("The value you indicated is " + str(isSpace) + "\n")

#adapted behavior keeps side road lamps green for 1 min no matter the side road sensor
def modified_behavior():
    global mod_start_time
    global mod_max_time
    while  (time.time()-s_road_start_time)<s_road_max_time:
        setIsSpace()
        if isSpace == True:
            check_main_road()
        else:
            reset()
                     
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

def check_main_road():
    setMainRoad1()
    if mainRoad1 == True:
        ret = client.publish ("hub-asri84368/mainRoad1", "red")
        print ("MainRoad1 set to red\n")
    setMainRoad2()
    if mainRoad2 == True:
        ret = client.publish ("hub-asri84368/mainRoad1", "red")
        print ("MainRoad2 set to red\n")
    ret = client.publish ("hub-asri84368/sideRoad", "green")
    print ("SideRoad set to green\n")

def reset():
    ret = client.publish ("hub-asri84368/mainRoad1", "green")
    print ("MainRoad1 set to green\n")
    ret = client.publish ("hub-asri84368/mainRoad2", "green")
    print ("MainRoad2 set to green\n")
    ret = client.publish ("hub-asri84368/sideRoad", "red")
    print ("SideRoad set to red\n")
    
#initialise lamps    
reset()

#initialise variables for while cycles and time restriction on side road value recording
setSideRoad()
setIsSpace()
s_road_start_time = time.time()

while True:
    try:
        if sideRoad == True:
            if isSpace == True:
                check_main_road()

        else:
            reset()
        
        setSideRoad()
        setIsSpace()
        #retains connection with MQTT Broker
        client.loop()

    except KeyboardInterrupt:
        print("Simulation exited. Connection is about to be closed.\n")
    except NameError:
        print("A local or global name is not found.\n")
    except SystemExit:
        print("Fatal error. sys.exit() was called.Traceback:\n")

#exit infinite while loop and close connection
client.disconnect ()
    



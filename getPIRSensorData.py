import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

GPIO.setup(3, GPIO.IN)
try:
    print ("PIR Module Test (CTRL+C to exit)")
    time.sleep(2)
    print ("Ready")
    
    while True:
        if GPIO.input(3):
           print("Motion detected!")
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Out")
    GPIO.cleanup()

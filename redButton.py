import RPi.GPIO as GPIO
from time import sleep

print("Red Button")

def error():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    LED=17
    Buzzer=13

    GPIO.setup(Buzzer,GPIO.OUT) 
    GPIO.setup(LED,GPIO.OUT)

    GPIO.output(LED,GPIO.HIGH)
    GPIO.output(Buzzer,GPIO.HIGH)
    sleep(2)
    GPIO.output(LED,GPIO.LOW)
    GPIO.output(Buzzer,GPIO.LOW)
    GPIO.cleanup()
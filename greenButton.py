print("Green Button")

import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED=18

GPIO.setup(LED,GPIO.OUT)

GPIO.output(LED,GPIO.HIGH)
sleep(2)
GPIO.output(LED,GPIO.LOW)

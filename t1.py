import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(20, GPIO.OUT) #DATA
GPIO.setup(22, GPIO.OUT) #LE
GPIO.setup(21, GPIO.OUT) #CLK
GPIO.setup(23, GPIO.OUT) #OE1
GPIO.setup(24, GPIO.OUT) #OE2
GPIO.setup(25, GPIO.OUT) #OE3

GPIO.output(26, GPIO.IN) #button1
GPIO.output(27, GPIO.IN) #button2

GPIO.output(22, GPIO.LOW)

GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.HIGH)
GPIO.output(25, GPIO.HIGH)

def funZapal():
    for i in range(0,48)
    GPIO.output(20, GPIO.HIGH)
    GPIO.output(21, GPIO.LOW)
    GPIO.output(21, GPIO.HIGH)
    sleep(0.1)
    GPIO.output(22, GPIO.HIGH)
   
while True:
    print(GPIO.input(26))
    
while True:
    if (GPIO.input(26) == 0):
        funZapal()


GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.LOW)
GPIO.output(25, GPIO.LOW)

#GPIO.output(20, GPIO.LOW)
#GPIO.output(21, GPIO.LOW)
#GPIO.output(22, GPIO.LOW)

print("leci")
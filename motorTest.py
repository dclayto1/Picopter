#RED MOTORS - CLOCKWISE
#WHITE MOTORS - COUNTER-CLOCKWISE

import RPi.GPIO as GPIO

chan = [13,29,33,40]
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
for each in chan:
    GPIO.setup(each, GPIO.OUT)

m1 = GPIO.PWM(13, 50) #WHITE
m2 = GPIO.PWM(29, 50) #RED
m3 = GPIO.PWM(33, 50) #WHITE
m4 = GPIO.PWM(40, 50) #RED

motorList = [m1, m2, m3, m4]
for each in motorList:
    each.start(5.0) #5.0 is the "0" throttle

loop = True
while loop:

    #6.0 appears to stop the motor as well, and greater than 11 was too high
    speed = input("Enter speed value 6.2<speed<11: ")
    if(speed == 0):
        loop = False
    elif(speed < 5.0 or speed > 20.0):
        print "Invalid speed entered."
    else:
        for each in motorList:
            each.ChangeDutyCycle(speed)


#stop all the motors
for each in motorList:
    #each.stop()
    each.ChangeDutyCycle(5.0) #stops them without the invalid input signal beeping

#cleanup
GPIO.cleanup()

from Tkinter import *
import RPi.GPIO as GPIO
import smbus

import math
import time

#GPIO pins
M1 = 13#white
M3 = 33#white

GPIO.setmode(GPIO.BOARD)
GPIO.setup(M1, GPIO.OUT)
GPIO.setup(M3, GPIO.OUT)


motor1 = GPIO.PWM(M1, 50)
motor3 = GPIO.PWM(M3, 50)


motor1Speed=0
motor3Speed=0


#0%-100% scale...5.0=0%, starting at 6.2, every 0.038 is 1%, 10.0 is 100%
ZERO = 5.0
PWM_SCALE = 0.038
PWM_MAX = 10.0
PWM_MIN = 6.2
INCREASE = 1.0
DECREASE = -1.0


#Power management registers
power_mgmt_1 = 0x6b
power_mgmt_0 = 0x6c

bus = smbus.SMBus(1) #1 if Revision2 board, 0 if original board
address = 0x68 #0x68 if AD0 is grounded, otherwise 0x69 if 3.3v

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a, b):
    return math.sqrt((a*a) + (b*b))

def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)

def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)






def copterLoop(screen):
	print "CopterLoop"
	screen.after(1, copterLoop(screen))



def gui():
	screen = Tk()	
	screen.title("Picopter")
	screen.minsize(640,480)
	screen.resizable(width=False, height=False)


	def startFunc():
		print "startFunc"
		motor1.start(ZERO)
		motor3.start(ZERO)
	#####


	def changeMotor(motor, change):
		if(motor == motor1):
			if(change == DECREASE):
				print "motor1 decreased"
				if(motor1Speed == PWM_MIN):
					motor1Speed = ZERO
					decreaseMotor1Button["state"] = "disabled"
				else:
					motor1Speed -= PWM_SCALE
					if(motor1Speed <= PWM_MIN):
						motor1Speed = PWM_MIN

				if(increaseMotor1Button["state"] == "disabled"):
					increaseMotor1Button["state"] = "normal"

			else:
				print "motor1 increased"
				if(motor1Speed == ZERO):
					motor1Speed = PWM_MIN
				else:
					motor1Speed += PWM_SCALE
					if(motor1Speed >= PWM_MAX):
						motor1Speed = PWM_MAX
						increaseMotor1Button["state"] = "disabled"
		
				if(decreaseMotor1Button["state"] == "disabled"):
					decreaseMotor1Button["state"] = "normal"

			motorSpeed = motor1Speed


		else:
			if(change == DECREASE):
				print "motor3 decreased"
				if(motor3Speed == PWM_MIN):
					motor3Speed = ZERO
					decreaseMotor3Button["state"] = "disabled"
				else:
					motor3Speed -= PWM_SCALE
					if(motor3Speed <= PWM_MIN):
						motor3Speed = PWM_MIN

				if(increaseMotor3Button["state"] == "disabled"):
					increaseMotor3Button["state"] = "normal"

			else:
				print "motor3 increased"
				if(motor3Speed == ZERO):
					motor3Speed = PWM_MIN
				else:
					motor3Speed += PWM_SCALE
					if(motor3Speed >= PWM_MAX):
						motor3Speed = PWM_MAX
						increaseMotor3Button["state"] = "disabled"
		
				if(decreaseMotor3Button["state"] == "disabled"):
					decreaseMotor3Button["state"] = "normal"

			motorSpeed = motor3Speed


		motor.ChangeDutyCycle(motorSpeed)
	#####

	def changeMotors(change):
		if(change == DECREASE):
			print "both motors decreased"
		else:
			print "both motors increased"
		changeMotor(motor1, change)
		changeMotor(motor3, change)
	#####


	def stopFunc():
		print "stopFunc"
		motor1.ChangeDutyCycle(ZERO)
		motor3.ChangeDutyCycle(ZERO)
		GPIO.cleanup()
	#####

	#STATE BUTTONS
	startButton = Button(screen, text="Start", command=startFunc)
	startButton.pack()
	stopButton = Button(screen, text="Stop", command=stopFunc)
	stopButton.pack()
	#INCREASE BUTTONS
	increaseMotor1Button = Button(screen, text="Increase M1", command=lambda:changeMotor(motor1, INCREASE))
	increaseMotor1Button.pack()
	increaseMotor3Button = Button(screen, text="Increase M3", command=lambda:changeMotor(motor3, INCREASE))
	increaseMotor3Button.pack()
	increaseMotorsButton = Button(screen, text="Increase Motors", command=lambda:changeMotors(INCREASE))
	increaseMotorsButton.pack()
	#DECREASE BUTTONS
	decreaseMotor1Button = Button(screen, text="Decrease M1", command=lambda:changeMotor(motor1, DECREASE))
	decreaseMotor1Button.pack()
	decreaseMotor3Button = Button(screen, text="Decrease M3", command=lambda:changeMotor(motor3, DECREASE))
	decreaseMotor3Button.pack()
	decreaseMotorsButton = Button(screen, text="Decrease Motors", command=lambda:changeMotors(DECREASE))
	decreaseMotorsButton.pack()


	#screen.after(1, copterLoop(screen))
	screen.mainloop()



def main():
	print "main"
	gui()
	print "complete"


main()
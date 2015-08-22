import RPi.GPIO as GPIO
import smbus
import math
import time
import socket
import threading


###################################################################
## Globals
###################################################################
#GPIO pins
M1 = 13#white
M2 = 29#red
M3 = 33#white
M4 = 40#red

GPIO.setmode(GPIO.BOARD)
GPIO.setup(M1, GPIO.OUT)
GPIO.setup(M2, GPIO.OUT)
GPIO.setup(M3, GPIO.OUT)
GPIO.setup(M4, GPIO.OUT)

motor1 = GPIO.PWM(M1, 50)
motor2 = GPIO.PWM(M2, 50)
motor3 = GPIO.PWM(M3, 50)
motor4 = GPIO.PWM(M4, 50)

motor1Speed=0.0
motor2Speed=0.0
motor3Speed=0.0
motor4Speed=0.0

#Motor lists -> [ name, GPIO-pin, motor, speed ]
NAME=0
PIN=1
MOTOR=2
SPEED=3
motor1List = [ "Motor1", M1, motor1, motor1Speed ]
motor2List = [ "Motor2", M2, motor2, motor2Speed ]
motor3List = [ "Motor3", M3, motor3, motor3Speed ]
motor4List = [ "Motor4", M4, motor4, motor4Speed ]


#0%-100% scale...5.0=0%, starting at 6.2, every 0.038 is 1%, 10.0 is 100%
ZERO = 5.0
PWM_SCALE = 0.038
PWM_MAX = 10.0
PWM_MIN = 6.2
INCREASE = 1.0
DECREASE = -1.0
###################################################################
###################################################################


###################################################################
## Socket Thread
###################################################################
def remoteCommands():
	#valid incoming messages - all messages are 8 characters
	#motor messages will be the motor, a space, and the change
	#i.e. "MOTORA +" will increase all motors
	msg_ALL="MOTORA"
	msg_X="MOTORX"
	msg_Y="MOTORY"
	msg_M1="MOTOR1"
	msg_M2="MOTOR2"
	msg_M3="MOTOR3"
	msg_M4="MOTOR4"
	msg_INCREASE="+"
	msg_DECREASE="-"
	msg_STOP="STOPALL!"
	#####

	loop=True
	HOST=''
	PORT=56789
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))

	while loop:
		s.listen(1)
		conn, addr = s.accept()
		data = conn.recv(8)
		data = data.split()
		if(len(data) == 1):
			if(data[0] == msg_STOP):
				stopFunc()
			else:
				print "Invalid message"
		elif(len(data) == 2):
			if(data[0] == msg_ALL): #All motors
				if(data[1] == msg_INCREASE):
					changeMotorsALL(INCREASE)
				elif(data[1] == msg_DECREASE):
					changeMotorsALL(DECREASE)
				else:
					print "Invalid message"
			elif(data[0] == msg_X): #Motors over X rotation
				if(data[1] == msg_INCREASE):
					changeMotorsXrotation(INCREASE)#backwards
				elif(data[1] == msg_DECREASE):
					changeMotorsXrotation(DECREASE)#forwards
				else:
					print "Invalid message"
			elif(data[0] == msg_Y): #Motors over Y rotation
				if(data[1] == msg_INCREASE):
					changeMotorsYrotation(INCREASE)#right
				elif(data[1] == msg_DECREASE):
					changeMotorsYrotation(DECREASE)#left
				else:
					print "Invalid message"
			elif(data[0] == msg_M1): #Motor 1
				if(data[1] == msg_INCREASE):
					changeMotor(motor1List, INCREASE)
				elif(data[1] == msg_DECREASE):
					changeMotor(motor1List, DECREASE)
				else:
					print "Invalid message"
			elif(data[0] == msg_M2): #Motor 2
				if(data[1] == msg_INCREASE):
					changeMotor(motor2List, INCREASE)
				elif(data[1] == msg_DECREASE):
					changeMotor(motor2List, DECREASE)
				else:
					print "Invalid message"
			elif(data[0] == msg_M3): #Motor 3
				if(data[1] == msg_INCREASE):
					changeMotor(motor3List, INCREASE)
				elif(data[1] == msg_DECREASE):
					changeMotor(motor3List, DECREASE)
				else:
					print "Invalid message"
			elif(data[0] == msg_M4): #Motor 4
				if(data[1] == msg_INCREASE):
					changeMotor(motor4List, INCREASE)
				elif(data[1] == msg_DECREASE):
					changeMotor(motor4List, DECREASE)
				else:
					print "Invalid message"
			else:
				print "Invalid message"
		else:
			print "Invalid message"



###################################################################
###################################################################




###################################################################
## Accelerometer/Gyroscope
###################################################################
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
###################################################################
###################################################################



###################################################################
## Interactive functions
###################################################################
def startFunc():
	print "Initialized all motors to speed = 0%"
	motor1List[SPEED]=ZERO
	motor2List[SPEED]=ZERO
	motor3List[SPEED]=ZERO
	motor4List[SPEED]=ZERO
	motor1List[MOTOR].start(motor1List[SPEED])
	motor2List[MOTOR].start(motor2List[SPEED])
	motor3List[MOTOR].start(motor3List[SPEED])
	motor4List[MOTOR].start(motor4List[SPEED])
#####

def changeMotor(motorList, change):
	oldSpeed = motorList[SPEED]
	if(change == DECREASE): #Decrease
		if(motorList[SPEED] == PWM_MIN):
			motorList[SPEED] = ZERO
		else:
			motorList[SPEED] -= PWM_SCALE
			if(motorList[SPEED] <= PWM_MIN):
				motorList[SPEED] = PWM_MIN
	else: #Increase
		if(motorList[SPEED] == ZERO):
			motorList[SPEED] = PWM_MIN
		else:
			motorList[SPEED] += PWM_SCALE
			if(motorList[SPEED] >= PWM_MAX):
				motorList[SPEED] = PWM_MAX

	motorList[MOTOR].ChangeDutyCycle(motorList[SPEED])
	print "%s speed changed from %f to %f" % (motorList[NAME], oldSpeed, motorList[SPEED])
#####

def changeMotorsXrotation(change):
	changeMotor(motor1List, change)
	changeMotor(motor2List, change)
	changeMotor(motor3List, -change)
	changeMotor(motor4List, -change)

def changeMotorsYrotation(change):
	changeMotor(motor1List, change)
	changeMotor(motor4List, change)
	changeMotor(motor2List, -change)
	changeMotor(motor3List, -change)

def changeMotorsALL(change):
	changeMotor(motor1List, change)
	changeMotor(motor2List, change)
	changeMotor(motor3List, change)
	changeMotor(motor4List, change)
#####

def stopFunc():
	print "Stopping all motors, speeds = 0%"
	motor1List[SPEED]=ZERO
	motor2List[SPEED]=ZERO
	motor3List[SPEED]=ZERO
	motor4List[SPEED]=ZERO
	motor1List[MOTOR].ChangeDutyCycle(motor1List[SPEED])
	motor2List[MOTOR].ChangeDutyCycle(motor2List[SPEED])
	motor3List[MOTOR].ChangeDutyCycle(motor3List[SPEED])
	motor4List[MOTOR].ChangeDutyCycle(motor4List[SPEED])
#####
###################################################################
###################################################################






def main():
	t = threading.Thread(target=remoteCommands, args=())
	t.start()


	GPIO.cleanup()
	t.join()

main()
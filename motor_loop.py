import RPi.GPIO as GPIO
import smbus
import math
import time
import socket
import threading
import signal
import sys


###################################################################
## Globals
###################################################################
#LOOP[0] for thread cleanup
LOOP = [True]

#Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


###################################################################
#0%-100% scale...5.0=0%, starting at 6.2, every 0.038 is 1%, 10.0 is 100%
ZERO = 5.0
PWM_SCALE = 0.038
PWM_MAX = 10.0
PWM_MIN = 6.2
INCREASE = 1.0
DECREASE = -1.0
###################################################################
###################################################################


#GPIO pins
M1 = 13#white
M2 = 29#red
M3 = 33#white
M4 = 40#red

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(M1, GPIO.OUT)
GPIO.setup(M2, GPIO.OUT)
GPIO.setup(M3, GPIO.OUT)
GPIO.setup(M4, GPIO.OUT)

motor1 = GPIO.PWM(M1, 50)
motor2 = GPIO.PWM(M2, 50)
motor3 = GPIO.PWM(M3, 50)
motor4 = GPIO.PWM(M4, 50)

motor1Speed=ZERO
motor2Speed=ZERO
motor3Speed=ZERO
motor4Speed=ZERO
motor1_adjustedSpeed=motor1Speed
motor2_adjustedSpeed=motor2Speed
motor3_adjustedSpeed=motor3Speed
motor4_adjustedSpeed=motor4Speed

#Motor lists -> [ name, GPIO-pin, motor, speed, adjustedSpeed ] #adjustedspeed is the change to the base speed for stabilization
NAME=0
PIN=1
MOTOR=2
SPEED=3
ADJUSTEDSPEED=4
motor1List = [ "Motor1", M1, motor1, motor1Speed, motor1_adjustedSpeed ]
motor2List = [ "Motor2", M2, motor2, motor2Speed, motor2_adjustedSpeed ]
motor3List = [ "Motor3", M3, motor3, motor3Speed, motor3_adjustedSpeed ]
motor4List = [ "Motor4", M4, motor4, motor4Speed, motor4_adjustedSpeed ]
motors = [ motor1List, motor2List, motor3List, motor4List ]
###################################################################
###################################################################




###################################################################
## Handle Signal Interrupt
###################################################################
def sigCleanup(signum, frame):
    cleanup()
    sys.exit(0)

def cleanup():
    print "Starting cleanup"
    LOOP[0]=False
    stopFunc()
    GPIO.cleanup()
    try:
        s.close()
    except Exception:
        print "No socket to close"
    
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
    msg_START="STARTALL"
    msg_FINISH="FINISH!!"
    #####


    HOST=''
    PORT=56789
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept() #Hangs here occasionally on a Ctrl+C
    while LOOP[0]:
        
        data = conn.recv(8)
        if not data: break
        data = data.split()
        if(len(data) == 1):
            if(data[0] == msg_STOP): #Stop all motors
                stopFunc()
                #s.close()
                #LOOP[0]=False
            elif(data[0] == msg_START): #Start all motors
                startFunc()
            elif(data[0] == msg_FINISH): #Finish thread
                stopFunc()
                s.close()
                LOOP[0]=False
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


    conn.close()

    print "Ending listening thread"

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
            if(motorList[SPEED] <= ZERO):
                motorList[SPEED] = ZERO
            elif(motorList[SPEED] <= PWM_MIN):
                motorList[SPEED] = PWM_MIN
    else: #Increase
        if(motorList[SPEED] == ZERO):
            motorList[SPEED] = PWM_MIN
        else:
            motorList[SPEED] += PWM_SCALE
            if(motorList[SPEED] >= PWM_MAX):
                motorList[SPEED] = PWM_MAX

    #motorList[MOTOR].ChangeDutyCycle(motorList[SPEED])
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
    '''motor1List[MOTOR].ChangeDutyCycle(motor1List[SPEED])
    motor2List[MOTOR].ChangeDutyCycle(motor2List[SPEED])
    motor3List[MOTOR].ChangeDutyCycle(motor3List[SPEED])
    motor4List[MOTOR].ChangeDutyCycle(motor4List[SPEED])'''
#####
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




def main(): 
    t.start()

    #Wake up the mpu6050 (it starts in sleep mode)
    bus.write_byte_data(address, power_mgmt_1, 0)

    #samplerate? and time constant?
    samplerate = 0.005 #loop was taking about .0052-.0058seconds for each iteration if print to terminal, .0047 if directed to file...rounded to .005
    timeconstant = 1.0
    alpha = timeconstant/(timeconstant+samplerate)
    #filtered_angle = alpha * (gyro_angle) + (1 - alpha) * (accel_angle)
    #gyro_angle = (previous filtered angle) + (angular_change)*(samplerate)


    #initialize rotation
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)

    accel_xout_scaled = read_word_2c(0x3b) / 16384.0
    accel_yout_scaled = read_word_2c(0x3d) / 16384.0
    accel_zout_scaled = read_word_2c(0x3f) / 16384.0
    x_rotation = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    y_rotation = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

    filtered_x_rotation = x_rotation
    filtered_y_rotation = y_rotation

    # PID values
    X_ROTATION_OFFSET = -3.1 #+/- 0.2 after letting it run on a flat surface for a while
    Y_ROTATION_OFFSET = 0.15 #+/- 0.2 after letting it run on a flat surface for a while
    SET_POINT = 0.0 #leveled #using the same SP for both X and Y axises
    K_PROPORTIONAL = 1.0
    K_INTEGRAL = 0.0
    K_DERIVATIVE = 0.0
    error_X_axis = 0.0
    error_Y_axis = 0.0
    dt = 0.0
    integral_X_axis = 0.0
    integral_Y_axis = 0.0


    loopstart = time.time()
    while 1:
        print time.time() - loopstart
        loopstart = time.time()

        gyro_x_rotation = filtered_x_rotation + ((read_word_2c(0x43)/131) * samplerate)
        gyro_y_rotation = filtered_y_rotation + ((read_word_2c(0x45)/131) * samplerate)
        
        accel_xout_scaled = read_word_2c(0x3b) / 16384.0
        accel_yout_scaled = read_word_2c(0x3d) / 16384.0
        accel_zout_scaled = read_word_2c(0x3f) / 16384.0
        x_rotation = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled) - X_ROTATION_OFFSET
        y_rotation = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled) - Y_ROTATION_OFFSET

        filtered_x_rotation = (alpha * gyro_x_rotation) + ((1-alpha) * (x_rotation))
        filtered_y_rotation = (alpha * gyro_y_rotation) + ((1-alpha) * (y_rotation))

        print "x rotation - %f" % filtered_x_rotation
        print "y rotation - %f" % filtered_y_rotation

        #PID
        dt = time.time() - loopstart
        error_X_axis = SET_POINT - (filtered_x_rotation)
        error_Y_axis = SET_POINT - (filtered_y_rotation)
        print "X_error " + str(error_X_axis)
        print "Y_error " + str(error_Y_axis)
        integral_X_axis+=(dt*error_X_axis)
        integral_Y_axis+=(dt*error_Y_axis)
        process_variable_X_axis = (K_PROPORTIONAL*error_X_axis) + (K_INTEGRAL*(integral_X_axis)) #just PI in PID for now
        process_variable_Y_axis = (K_PROPORTIONAL*error_Y_axis) + (K_INTEGRAL*(integral_Y_axis)) #just PI in PID for now

        
        motor1List[ADJUSTEDSPEED] = motor1List[SPEED]
        motor2List[ADJUSTEDSPEED] = motor2List[SPEED]
        motor3List[ADJUSTEDSPEED] = motor3List[SPEED]
        motor4List[ADJUSTEDSPEED] = motor4List[SPEED]
        
        motor1List[ADJUSTEDSPEED] += (process_variable_X_axis*(PWM_SCALE*PWM_SCALE))
        motor2List[ADJUSTEDSPEED] += (process_variable_X_axis*(PWM_SCALE*PWM_SCALE))
        motor3List[ADJUSTEDSPEED] -= (process_variable_X_axis*(PWM_SCALE*PWM_SCALE))
        motor4List[ADJUSTEDSPEED] -= (process_variable_X_axis*(PWM_SCALE*PWM_SCALE))

        motor1List[ADJUSTEDSPEED] += (process_variable_Y_axis*(PWM_SCALE*PWM_SCALE))
        motor2List[ADJUSTEDSPEED] -= (process_variable_Y_axis*(PWM_SCALE*PWM_SCALE))
        motor3List[ADJUSTEDSPEED] -= (process_variable_Y_axis*(PWM_SCALE*PWM_SCALE))
        motor4List[ADJUSTEDSPEED] += (process_variable_Y_axis*(PWM_SCALE*PWM_SCALE))


        for each in motors:
            if(each[SPEED] == ZERO):
                each[ADJUSTEDSPEED] = ZERO
                each[MOTOR].ChangeDutyCycle(each[ADJUSTEDSPEED])
            elif(each[ADJUSTEDSPEED] < PWM_MIN):
                each[ADJUSTEDSPEED] = PWM_MIN
                each[MOTOR].ChangeDutyCycle(each[ADJUSTEDSPEED])
            elif(each[ADJUSTEDSPEED] > PWM_MAX):
                each[ADJUSTEDSPEED] = PWM_MAX
                each[MOTOR].ChangeDutyCycle(each[ADJUSTEDSPEED])
            else:
                each[MOTOR].ChangeDutyCycle(each[ADJUSTEDSPEED])


        print "M1: %f | M2: %f | M3: %f | M4: %f" % (motor1List[SPEED], motor2List[SPEED], motor3List[SPEED], motor4List[SPEED])
        print "M1: %f | M2: %f | M3: %f | M4: %f" % (motor1List[ADJUSTEDSPEED], motor2List[ADJUSTEDSPEED], motor3List[ADJUSTEDSPEED], motor4List[ADJUSTEDSPEED])



        if(threading.activeCount() == 1):
            print "Thread finished"
            break

    cleanup()



t = threading.Thread(target=remoteCommands, args=())
signal.signal(signal.SIGINT, sigCleanup)
main()
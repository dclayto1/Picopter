import RPi.GPIO as GPIO
import smbus
import math
import time

#GPIO pins
M1 = 13#white
M2 = 29#red
M3 = 33#white
M4 = 40#red

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




def main():

    #setup the GPIO pins for use
    chan = [M1, M2, M3, M4]
    GPIO.cleanup() #cleanup pins that may not have been cleaned up previously
    GPIO.setmode(GPIO.BOARD)
    for each in chan:
        GPIO.setup(each, GPIO.OUT)

    motor1 = GPIO.PWM(M1, 50)
    motor2 = GPIO.PWM(M2, 50)
    motor3 = GPIO.PWM(M3, 50)
    motor4 = GPIO.PWM(M4, 50)

    #initialize the ESC's for the motors
    motorList = [motor1, motor2, motor3, motor4]

    #index 0 for negative rotation, index 1 for positive rotation
    motorX = [[motor1, motor2], [motor3, motor4]]
    motorY = [[motor1, motor4], [motor2, motor3]]
    for each in motorList:
        each.start(5.0) #5.0 is the "0" throttle

    #Wake up the mpu6050 (it starts in sleep mode)
    bus.write_byte_data(address, power_mgmt_1, 0)

    
    print "This test is designed to test the stabilization."
    raw_input("Press 'Enter' when you're ready to begin...")

    #start motors, not high enough to lift off yet so no worries
    throttle_speed = 7.1
    for each in motorList:
        each.ChangeDutyCycle(throttle_speed)
    
    #samplerate? and time constant?
    samplerate = 0.005 #loop was taking about .0047seconds for each iteration, rounded up
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
    time.sleep(10)

    origin = time.time()

    #stabilization loop
    loop = True 
    while loop:
        start = time.time()
        gyro_x_rotation = filtered_x_rotation + ((read_word_2c(0x43)/131) * samplerate)
        gyro_y_rotation = filtered_y_rotation + ((read_word_2c(0x45)/131) * samplerate)
        
        accel_xout_scaled = read_word_2c(0x3b) / 16384.0
        accel_yout_scaled = read_word_2c(0x3d) / 16384.0
        accel_zout_scaled = read_word_2c(0x3f) / 16384.0
        x_rotation = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y_rotation = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

        filtered_x_rotation = (alpha * gyro_x_rotation) + ((1-alpha) * (x_rotation))
        filtered_y_rotation = (alpha * gyro_y_rotation) + ((1-alpha) * (y_rotation))

        print "x rotation - %f" % filtered_x_rotation
        print "y rotation - %f" % filtered_y_rotation
        print "time: %f" % (time.time()-start)

    
        motor1_speed = throttle_speed
        motor2_speed = throttle_speed
        motor3_speed = throttle_speed
        motor4_speed = throttle_speed
        #stabilize over X-axis, giving a 5 degree error on both sides
        if(filtered_x_rotation < -5.0):
            motor1_speed += 0.1
            motor2_speed += 0.1
        elif(filtered_x_rotation > 5.0):
            motor3_speed += 0.1
            motor4_speed += 0.1

        #stabilize over Y-axis, giving a 5 degree error on both sides
        if(filtered_y_rotation < -5.0):
            motor1_speed += 0.1
            motor4_speed += 0.1
        elif(filtered_y_rotation > 5.0):
            motor2_speed += 0.1
            motor3_speed += 0.1


        motor1.ChangeDutyCycle(motor1_speed)
        motor2.ChangeDutyCycle(motor2_speed)
        motor3.ChangeDutyCycle(motor3_speed)
        motor4.ChangeDutyCycle(motor4_speed)

        if(time.time()-origin > 10.0):
            break


    lower = time.time()
    for each in motorList:
        each.ChangeDutyCycle(6.4)
    while 1:
        if(time.time() - lower > 10.0):
            break

    for each in motorList:
        each.stop() #Will re-enable the beeping, since no valid signal to ESC

    #cleanup
    GPIO.cleanup()
####################
#End Main




main()

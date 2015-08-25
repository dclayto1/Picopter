from Tkinter import *
import signal
import socket

HOST = "192.168.0.200"
PORT = 56789

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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


def gui():
	screen = Tk()	
	screen.title("Picopter")
	screen.minsize(640,480)
	screen.resizable(width=False, height=False)
	
	

	def startFunc():
		s.sendall(msg_START)

	def changeMotor(motor, change):
		s.sendall(motor+" "+change)

	def stopFunc():
		s.sendall(msg_STOP)

	def finish():
		s.sendall(msg_FINISH)
		s.close()
		screen.destroy()

	screen.protocol('WM_DELETE_WINDOW', finish)


	#STATE BUTTONS
	startButton = Button(screen, text="Start", command=startFunc)
	startButton.pack()
	stopButton = Button(screen, text="Stop", command=stopFunc)
	stopButton.pack()
	#INCREASE BUTTONS
	increaseMotor1Button = Button(screen, text="Increase M1", command=lambda:changeMotor(msg_M1, msg_INCREASE))
	increaseMotor1Button.pack()
	increaseMotor2Button = Button(screen, text="Increase M2", command=lambda:changeMotor(msg_M2, msg_INCREASE))
	increaseMotor2Button.pack()
	increaseMotor3Button = Button(screen, text="Increase M3", command=lambda:changeMotor(msg_M3, msg_INCREASE))
	increaseMotor3Button.pack()
	increaseMotor4Button = Button(screen, text="Increase M4", command=lambda:changeMotor(msg_M4, msg_INCREASE))
	increaseMotor4Button.pack()
	increaseMotorsButton = Button(screen, text="Increase All Motors", command=lambda:changeMotor(msg_ALL, msg_INCREASE))
	increaseMotorsButton.pack()
	#DECREASE BUTTONS
	decreaseMotor1Button = Button(screen, text="Decrease M1", command=lambda:changeMotor(msg_M1, msg_DECREASE))
	decreaseMotor1Button.pack()
	decreaseMotor2Button = Button(screen, text="Decrease M2", command=lambda:changeMotor(msg_M2, msg_DECREASE))
	decreaseMotor2Button.pack()
	decreaseMotor3Button = Button(screen, text="Decrease M3", command=lambda:changeMotor(msg_M3, msg_DECREASE))
	decreaseMotor3Button.pack()
	decreaseMotor4Button = Button(screen, text="Decrease M4", command=lambda:changeMotor(msg_M4, msg_DECREASE))
	decreaseMotor4Button.pack()
	decreaseMotorsButton = Button(screen, text="Decrease Motors", command=lambda:changeMotor(msg_ALL, msg_DECREASE))
	decreaseMotorsButton.pack()


	#screen.after(1, copterLoop(screen))
	screen.mainloop()


def cleanup():
	s.sendall(msg_FINISH)
	s.close()

def sigCleanup(signum, frame):
	cleanup()
	sys.exit()


def main():
	print "main"
	gui()
	print "complete"


signal.signal(signal.SIGINT, sigCleanup)
main()
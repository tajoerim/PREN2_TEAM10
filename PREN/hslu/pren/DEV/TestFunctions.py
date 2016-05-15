import serial

port = raw_input("Enter TTY Port: ")

ser = serial.Serial('/dev/tty' + str(port), 9600)

run = True
while (run):
    cmd = raw_input("Enter Command: ")

    if (str(cmd) == "open"):
        ser.write("openCloseGrabber;2;")
        print ser.readline()

    elif (str(cmd) == "close"):
        ser.write("openCloseGrabber;1;")
        print ser.readline()

    elif (str(cmd) == "up"):
        cnt = raw_input("How many times?: ")
        for x in range(0, int(cnt)):
            ser.write("setGrabberPosition;0;1;")
            print ser.readline()

    elif (str(cmd) == "down"):
        cnt = raw_input("How many times?: ")
        for x in range(0, int(cnt)):
            ser.write("setGrabberPosition;0;2;")
            print ser.readline()

    elif (str(cmd) == "left"):
        cnt = raw_input("How many times?: ")
        for x in range(0, int(cnt)):
            ser.write("setGrabberPosition;1;0;")
            print ser.readline()

    elif (str(cmd) == "right"):
        cnt = raw_input("How many times?: ")
        for x in range(0, int(cnt)):
            ser.write("setGrabberPosition;2;0;")
            print ser.readline()

    elif (str(cmd) == "empty"):
        ser.write("emptyContainer;")
        print ser.readline()

    elif (str(cmd) == "shutdown"):
        ser.write("shutdown;")
        print ser.readline()

    elif (str(cmd) == "initEngines"):
        speed = raw_input("How fast?: ")
        ser.write("initEngines;")
        print ser.readline()
        ser.write("setSpeedLeft;" + speed + ";")
        print ser.readline()
        ser.write("setSpeedRight;" + speed + ";")
        print ser.readline()

    elif (str(cmd) == "speedLeft"):
        speed = raw_input("How fast?: ")
        ser.write("setSpeedLeft;" + speed + ";")
        print ser.readline()

    elif (str(cmd) == "speedRight"):
        speed = raw_input("How fast?: ")
        ser.write("setSpeedRight;" + speed + ";")
        print ser.readline()

    elif (str(cmd) == "speedLeft"):
        speed = raw_input("How fast?: ")
        ser.write("setSpeedLeft;" + speed + ";")
        print ser.readline()

    elif (str(cmd) == "setSpeed"):
        speed = raw_input("How fast?: ")
        ser.write("setSpeedLeft;" + speed + ";")
        print ser.readline()
        ser.write("setSpeedRight;" + speed + ";")
        print ser.readline()

    elif (str(cmd) == "led"):
        color = raw_input("color: ")
        ser.write("LED;" + color + ";")
        print ser.readline()

    elif (str(cmd) == "dist"):
        ser.write("getDistance;" + color + ";")
        print ser.readline()
        print ser.readline()

    elif (str(cmd) == "exit"):
        run = False

    else:
        ser.write(cmd)
        print ser.readline()
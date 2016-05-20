import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)

cnt = 0
curve = 1
   
cnt = 0 
while (True):
    cnt = cnt + 1

    if (curve == 1):
        curve = 2
    elif (curve == 2):
        curve = 3
    elif (curve == 3):
        curve = 4
    elif (curve == 4):
        curve = 1

    ser.write("driveCurve;" + str(curve) + ";")

    # print"|||| " + str(cnt)

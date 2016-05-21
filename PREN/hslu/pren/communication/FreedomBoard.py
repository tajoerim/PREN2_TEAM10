﻿'''
Created on 08.12.2015

@author: Christoph
'''

from hslu.pren.common import Logger
import hslu.pren.common.Utilities
import wave
from hslu.pren.common import Utilities
from _random import Random
import serial
import time
import sys
import threading
import inspect

lock = threading.Lock()

class FreedomBoardCommunicator():

    #Constructor
    def __init__(self, serialPortName="/dev/ttyACM0", baudRate="9600", raspberry=False):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        self.raspberry = raspberry
        self.previousAngle = 0
        self.speedActual = 5000
        self.speedLeft = 5000
        self.speedRight = 5000
        self.cntLeft = 0
        self.cntRight = 0
        self.cmdCount = 0
        self.logger = Logger.Logger("FRDM")
        if (self.raspberry):
            self.serial = serial.Serial(self.serialPortName, self.baudRate)

    #Remote Methods ------------------------------------
    
    def initEngines(self, speed=0):
        self.callRemoteMethod("initEngines", None)
        if (speed == 0):
            self.driveSpeedRamp(self.speedActual);
        else:
            self.driveSpeedRamp(speed);
        return;

    def stop(self):
        ret = self.callRemoteMethod("shutdown", None)
        time.sleep(0.5)
        return ret

    def setSpeed(self, speed, ramp=False):
        # print"[FRDM] set speed to:" + str(speed)

        if (self.speedLeft == speed and self.speedRight == speed):
            # print"[FRDM] Speed is equal to speedActual"
            return

        if (ramp):
            self.driveSpeedRamp(speed);

        self.speedActual = speed

    def driveSpeedRamp(self, speed):
        if (self.speedActual - speed > 5000): # Wenn die Differenz groesser als 5000 ist
            while (self.speedActual > speed):
                if (self.speedActual - speed > 1000): # Solange wir jeweils 1000er Schritte gehen koennen
                    self.speedActual -= 1000
                    # print"[FRDM] speed ramp: " + str(self.speedActual)
                    self.callRemoteMethod("setSpeed", [self.speedActual])
                    self.speedLeft = self.speedActual
                    self.speedRight = self.speedActual
                    time.sleep(0.2)
                else:
                    self.speedActual = speed
                    # print"[FRDM] speed ramp: " + str(self.speedActual)
                    self.callRemoteMethod("setSpeed", [self.speedActual])
                    self.speedLeft = self.speedActual
                    self.speedRight = self.speedActual
        else:
            self.speedActual = speed
            # print"[FRDM] speed ramp: " + str(self.speedActual)
            self.callRemoteMethod("setSpeed", [self.speedActual])
            self.speedLeft = self.speedActual
            self.speedRight = self.speedActual


    def setDriveAngle(self, correction):
        
        if (self.speedActual <= 0):
            return

        #corr = int(correction * ((self.speedActual*0.0026)-0.3226)) # Mit Referenzwerten 35000 -> 90 & 5000 -> 10 berechnet (Lineare veränderung)
        corr = int(correction * 10) # Mit Referenzwerten 35000 -> 90 & 5000 -> 10 berechnet (Lineare veränderung)
        left = self.speedActual + corr
        right = self.speedActual - corr
            
        changed = False

        if (left < 3500): # wir dürfen nicht unter 3500 gelangen, sonst stoppt der Motor
            left = 3500

        if (right < 3500): # wir dürfen nicht unter 3500 gelangen, sonst stoppt der Motor
            right = 3500

        if (self.speedLeft != left):
            self.speedLeft = left
            self.callRemoteMethod("setSpeedLeft", [self.speedLeft])

        if (self.speedRight != right):
            self.speedRight = right
            self.callRemoteMethod("setSpeedRight", [self.speedRight])

        if (changed):
            print"[FRDM] Speed Left: " + str(self.speedLeft) + "  right: " + str(self.speedRight)

    def isBatteryLow(self):
        if (self.raspberry):
            return self.callRemoteMethod("battery", None)
        else:
            return 0
        
    def openGrabber(self):
        self.callRemoteMethod("openCloseGrabber", [2])
        return self.stop()
        
    def closeGrabber(self):
        self.callRemoteMethod("openCloseGrabber", [1])
        return self.stop()
        
    def emptyContainer(self):
        self.callRemoteMethod("emptyContainer", None)
        return self.stop()
    
    def getDistance(self):
        if (self.raspberry):
            return self.callRemoteMethod("getDistance", None, expectReturnValue = True)
        else:
            return 0;
        
    def getColor(self):
        if (self.raspberry):
            color = self.callRemoteMethod("getColor", None, expectReturnValue = True)
            self.serial.timeout = 1
            return color
        else:
            return "2";

    def getDistanceEnemy(self):
        res = 0
        range = 5
        for x in range(0, range):
            res += self.callRemoteMethod("getDistanceEnemy", None)

        return (res / range)

    def setLedRed(self):
        self.setLedColor(True, True, False);

    def setLedGreen(self):
        self.setLedColor(False, True, False);

    def setLedBlue(self):
        self.setLedColor(False, False, True);

    def setLedCyan(self):
        self.setLedColor(False, True, True);

    def setLedMagenta(self):
        self.setLedColor(True, False, True);

    def setLedYellow(self):
        self.setLedColor(True, True, False);

    def setLedWhite(self):
        self.setLedColor(True, True, True);

    def setLedOff(self):
        self.setLedColor(False, True, False);

    def setLedColor(self, redOn, greenOn, blueOn):

        if (redOn):
            self.callRemoteMethod("LED", [1])
        else:
            self.callRemoteMethod("LED", [4])

        if (greenOn):
            self.callRemoteMethod("LED", [2])
        else:
            self.callRemoteMethod("LED", [5])

        if (blueOn):
            self.callRemoteMethod("LED", [3])
        else:
            self.callRemoteMethod("LED", [6])

        return
    
    def unloadThrough(self):
        self.stop();
        return self.callRemoteMethod("unloadThrough", None)
        self.stop();
        
    def setGrabberPosition(self, hor, vert):
        return self.callRemoteMethod("setGrabberPosition", [hor, vert])
    
    #communication
    def callRemoteMethod(self, method, array_args, expectReturnValue = True):
        
        with lock:
            try:

                self.cmdCount += 1
                command = Utilities.SerializeMethodWithParameters(method, array_args)
        
                if (self.raspberry):

                    try:
                        if (self.serial.isOpen() == False):
                            self.serial.open()

                        self.serial.write(command)
                        time.sleep(0.01)
                        if (expectReturnValue):
                            ret = self.serial.readline()
                    
                            # print"Method " + method + " returned: " + ret

                            return Utilities.DeserializeMethodWithParameters(method, ret)
                        else:
                            return 1
                    except:
                        try:
                            self.serial.close()
                            self.serial = serial.Serial(self.serialPortName, self.baudRate)
                            self.serial.write(command)
                
                            if (expectReturnValue):
                                ret = self.serial.readline()

                                return Utilities.DeserializeMethodWithParameters(method, ret)
                            else:
                                return 1
                        except:
                            print"[FRDM] SORRY NO CHANCE TO COMMUNICATE WITH FREEDOM BOARD!"
                            self.serial.close()
                            self.serial = serial.Serial(self.serialPortName, self.baudRate)
                            return None
                else:
                    return 1

            except KeyboardInterrupt:
                return None


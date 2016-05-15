'''
Created on 08.12.2015

@author: Christoph
@todo: Methoden implementieren
'''

import hslu.pren.common.Utilities
import wave
from hslu.pren.common import Utilities
from _random import Random
import serial
import time
import sys


class FreedomBoardCommunicator():

    #Constructor
    def __init__(self, serialPortName="/dev/ttyACM0", baudRate="9600", raspberry=False):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        self.raspberry = raspberry
        self.previousAngle = 0
        self.speedActual = 10000
        self.cntLeft = 0
        self.cntRight = 0
        self.cmdCount = 0
        if (self.raspberry):
            self.serial = serial.Serial(self.serialPortName, self.baudRate)

    #Remote Methods ------------------------------------
    
    def initEngines(self, speed):
        self.callRemoteMethod("initEngines", None)
        self.driveSpeedRamp(speed);
        return;

    def stop(self):
        return self.callRemoteMethod("shutdown", None)

    def setSpeed(self, speed, ramp=False):
        print "[FRDM] set speed to:" + str(speed)

        if (ramp):
            self.driveSpeedRamp(speed);

        self.speedActual = speed

    def driveSpeedRamp(self, speed):
        if (self.speedActual - speed > 5000): # Wenn die Differenz groesser als 5000 ist
            while (self.speedActual > speed):
                if (self.speedActual - speed > 500): # Solange wir jeweils 500er Schritte gehen koennen
                    self.speedActual -= 500
                    print "[FRDM] speed ramp: " + str(self.speedActual)
                    self.callRemoteMethod("setSpeedLeft", [self.speedActual], debugInfo=False)
                    self.callRemoteMethod("setSpeedRight", [self.speedActual], debugInfo=False)
                    time.sleep(0.03)
                else:
                    self.speedActual = speed
                    print "[FRDM] speed ramp: " + str(self.speedActual)
                    self.callRemoteMethod("setSpeedLeft", [self.speedActual], debugInfo=False)
                    self.callRemoteMethod("setSpeedRight", [self.speedActual], debugInfo=False)
        else:
            self.speedActual = speed
            print "[FRDM] speed ramp: " + str(self.speedActual)
            self.callRemoteMethod("setSpeedLeft", [speed], debugInfo=False)
            self.callRemoteMethod("setSpeedRight", [speed], debugInfo=False)
    
    def setDriveAngle(self, correction):
        
        if (self.speedActual <= 0):
            return

        #corr = int(correction * ((self.speedActual*0.0026)-0.3226)) # Mit Referenzwerten 35000 -> 90 & 5000 -> 10 berechnet (Lineare veränderung)
        corr = int(correction * 10) # Mit Referenzwerten 35000 -> 90 & 5000 -> 10 berechnet (Lineare veränderung)
        left = self.speedActual + corr
        right = self.speedActual - corr

        if (left > self.speedActual):
            left = self.speedActual
            
        if (right > self.speedActual):
            right = self.speedActual
            

        if (left < 3300):
            left = 3300

        if (right < 3300):
            right < 3300

        self.callRemoteMethod("setSpeedRight", [left], debugInfo=False)
        self.callRemoteMethod("setSpeedLeft", [right], debugInfo=False)
        print "[FRDM] Speed Left: " + str(left) + "  right: " + str(right)

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
        ret = self.callRemoteMethod("getDistance", None, expectReturnValue = True)
        if (self.raspberry):
            self.serial.readall();
        else:
            return 1600;
        return ret
    
    def getDistanceEnemy(self):
        res = 0
        range = 5
        for x in range(0, range):
            res += self.callRemoteMethod("getDistanceEnemy", None)

        return (res / range)

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
        return self.callRemoteMethod("unloadThrough", None)
        
    def setGrabberPosition(self, hor, vert):
        #hor: 1 = richtung container, 2 = weg von container
        #vert: 1 = rauf, 2 = runter
        return self.callRemoteMethod("setGrabberPosition", [hor, vert])
    
    #communication
    def callRemoteMethod(self, method, array_args, debugInfo = True, expectReturnValue = True):
        
        try:

            self.cmdCount += 1
            command = Utilities.SerializeMethodWithParameters(method, array_args)
        
            if (debugInfo):
                print "[FRDM]  [ " + str(self.cmdCount) + " ] Calling remote method on frdm: " + command

            if (self.raspberry):

                try:
                    if (self.serial.isOpen() == False):
                        self.serial.open()

                    self.serial.write(command)
                    if (expectReturnValue):
                        ret = self.serial.readline()
                        if (ret and debugInfo):
                            print "[FRDM] Freedom board returned: " + ret
                    
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
                            if (ret and debugInfo):
                                print "[FRDM] Freedom board returned: " + ret
                        
                            return Utilities.DeserializeMethodWithParameters(method, ret)
                        else:
                            return 1
                    except:
                        print "[FRDM] SORRY NO CHANCE TO COMMUNICATE WITH FREEDOM BOARD!"
            else:
                return 1

        except KeyboardInterrupt:
            return None


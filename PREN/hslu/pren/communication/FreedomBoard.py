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


class FreedomBoardCommunicator():

    #Constructor
    def __init__(self, serialPortName="/dev/ttyACM0", baudRate="9600", raspberry=False):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        self.raspberry = raspberry
        self.previousAngle = 0
        self.speedActual = 0
        self.cntLeft = 0
        self.cntRight = 0
        self.cmdCount = 0
        if (self.raspberry):
            self.serial = serial.Serial(self.serialPortName, self.baudRate)

    #Remote Methods ------------------------------------
    
    def waitForRun(self):
        self.callRemoteMethod("initEngines", None)
        return True;

    def stop(self):
        return self.callRemoteMethod("shutdown", None)

    def setSpeed(self, speed):
        print "set speed to:" + str(speed)
        self.speedActual = speed
    
    def setDriveAngle(self, correction):
        
        print "actual:" + str(self.speedActual)
        if (self.speedActual <= 0):
            return

        corr = int(correction * ((self.speedActual*0.0026)-0.3226)) # Mit Referenzwerten 35000 -> 90 & 5000 -> 10 berechnet (Lineare veränderung)
        left = self.speedActual + corr
        right = self.speedActual - corr

        if (left > self.speedActual):
            left = self.speedActual
            
        if (right > self.speedActual):
            right = self.speedActual

        self.callRemoteMethod("setSpeedLeft", [left], debugInfo=False)
        self.callRemoteMethod("setSpeedRight", [right], debugInfo=False)
        print "Speed Left: " + str(left) + "  right: " + str(right)

    def isBatteryLow(self):
        if (self.raspberry):
            return self.callRemoteMethod("battery", None)
        else:
            return 0
        
    def openGrabber(self):
        self.callRemoteMethod("openCloseGrabber", [1])
        return self.stop()
        
    def closeGrabber(self, state):
        self.callRemoteMethod("openCloseGrabber", [2])
        return self.stop()
        
    def emptyContainer(self):
        self.callRemoteMethod("emptyContainer", None)
        return self.stop()
    
    def getDistance(self):
        return 1600
        #return self.callRemoteMethod("getDistance", None, expectReturnValue = True)
    
    def getDistanceEnemy(self):
        res = 0
        range = 5
        for x in range(0, range):
            res += self.callRemoteMethod("getDistanceEnemy", None)

        return (res / range)
    
    def unloadThrough(self):
        return self.callRemoteMethod("unloadThrough", None)
        
    def setGrabberPosition(self, hor, vert):
        #hor: 1 = richtung container, 2 = weg von container
        #vert: 1 = rauf, 2 = runter
        return self.callRemoteMethod("setGrabberPosition", [hor, vert])
    
    #communication
    def callRemoteMethod(self, method, array_args, debugInfo = True, expectReturnValue = True):
        
        self.cmdCount += 1
        command = Utilities.SerializeMethodWithParameters(method, array_args)
        
        if (debugInfo):
            print " [ " + str(self.cmdCount) + " ] Calling remote method on frdm: " + command

        if (self.raspberry):

            try:
                if (self.serial.isOpen() == False):
                    self.serial.open()

                self.serial.write(command)
                if (expectReturnValue):
                    ret = self.serial.readline()
                    if (ret and debugInfo):
                        print "Freedom board returned: " + ret

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
                            print "Freedom board returned: " + ret

                        return Utilities.DeserializeMethodWithParameters(method, ret)
                    else:
                        return 1
                except:
                    print "SORRY NO CHANCE TO COMMUNICATE WITH FREEDOM BOARD!"
        else:
            return 1


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
        args = [speed]
        self.speedActual = speed
        return self.callRemoteMethod("setSpeed", args)
    
    def setDriveAngle(self, correction):
        
        speed = self.speedActual - (correction * 10)
        if (speed < 0):
            speed = 0
        self.callRemoteMethod("setSpeedLeft", [speed], debugInfo=True)
        
        speed = self.speedActual + (correction * 10)
        if (speed < 0):
            speed = 0
        self.callRemoteMethod("setSpeedRight", [speed], debugInfo=True)
        
    def isBatteryLow(self):
        if (self.raspberry):
            return self.callRemoteMethod("battery", None)
        else:
            return 0
        
    def openGrabber(self):
        return self.callRemoteMethod("openCloseGrabber", [1])
        
    def closeGrabber(self, state):
        return self.callRemoteMethod("openCloseGrabber", [2])
        
    def emptyContainer(self):
        return self.callRemoteMethod("emptyContainer", None)
    
    def getDistance(self):
        return 100
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


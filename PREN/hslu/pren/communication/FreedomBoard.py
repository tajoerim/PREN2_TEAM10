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

    CMD_LEFT_TURN_1 = 1
    CMD_LEFT_TURN_2 = 4

    CMD_RIGHT_TURN_1 = 2
    CMD_RIGHT_TURN_2 = 3

    #Constructor
    def __init__(self, serialPortName="/dev/ttyACM0", baudRate="9600", raspberry=False):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        self.raspberry = raspberry
        self.previousAngle = 0
        self.speedActual = 0
        self.cntLeft = 0
        self.cntRight = 0
        if (self.raspberry):
            self.serial = serial.Serial(self.serialPortName, self.baudRate)

    #Remote Methods ------------------------------------
    
    def waitForRun(self):
        self.callRemoteMethod("initEngines", None, expectReturnValue = True)
        return True;

    def stop(self):
        return self.callRemoteMethod("shutdown", None)

    def setSpeed(self, speed):
        args = [speed]
        self.speedActual = speed
        return
        #return self.callRemoteMethod("setSpeed", args)
    
    def setDriveAngle(self, angle):

        if (self.previousAngle > 0 and angle < 0):
            self.setSpeed(self.speedActual) # Set both engines to the same speed
        elif (self.previousAngle < 0 and angle > 0):
            self.setSpeed(self.speedActual) # Set both engines to the same speed

        self.previousAngle = angle

        #if (angle != 0):
        if (angle > 0 and self.cntRight < 10):
            self.cntRight += 1
            self.cntLeft = 0
            self.setEngineRightSlow()
            #if (angle > 50):
            #    self.setEngineLeftFast()
            #print "Turn right"
        elif (self.cntLeft < 10):
            self.cntLeft += 1
            self.cntRight = 0
            self.setEngineLeftSlow()
            #if (angle < -50):
            #    self.setEngineRightFast()
            #print "Turn left"

        else:
            self.setSpeed(self.speedActual) # Set both engines to the same speed
            #print "Go straight ahead"
    
    def setEngineLeftSlow(self):
            self.callRemoteMethod("driveCurve", [self.CMD_LEFT_TURN_1], debugInfo=False)
    
    def setEngineRightSlow(self):
            self.callRemoteMethod("driveCurve", [self.CMD_RIGHT_TURN_1], debugInfo=False)
    
    def setEngineLeftFast(self):
            self.callRemoteMethod("driveCurve", [self.CMD_RIGHT_TURN_2], debugInfo=False)
    
    def setEngineRightFast(self):
            self.callRemoteMethod("driveCurve", [self.CMD_LEFT_TURN_2], debugInfo=False)
        
    def isBatteryLow(self):
        if (self.raspberry):
            return self.callRemoteMethod("battery", None, expectReturnValue = True)
        else:
            return 0
        
    def openGrabber(self):
        return self.callRemoteMethod("openCloseGrabber", [1])
        
    def closeGrabber(self):
        return self.callRemoteMethod("openCloseGrabber", [0])
        
    def clearContainer(self):
        return self.callRemoteMethod("clearContainer", None)
    
    def getDistance(self):
        return 100
        #return self.callRemoteMethod("getDistance", None, expectReturnValue = True)
    
    def openThrough(self):
        return self.callRemoteMethod("openCloseThrough", [1])
    
    def closeThrough(self):
        return self.callRemoteMethod("openCloseThrough", [0])
        
    def setGrabberPosition(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def resetGrabberPosition(self):
        raise NotImplementedError( "Should have implemented this" )
    
    #communication
    def callRemoteMethod(self, method, array_args, debugInfo = True, expectReturnValue = False):
        command = Utilities.SerializeMethodWithParameters(method, array_args)
        
        if (debugInfo):
            print "Calling remote method on frdm: " + command

        if (self.raspberry):

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
        else:
            return 1


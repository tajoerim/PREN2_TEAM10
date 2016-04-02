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

    CMD_LEFT_TURN = 1
    CMD_RIGHT_TURN = 2

    #Constructor
    def __init__(self, serialPortName="/dev/ttyACM0", baudRate="9600", raspberry=False):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        self.raspberry = raspberry
        if (self.raspberry):
            self.serial = serial.Serial(self.serialPortName, self.baudRate, timeout=0.5)
    

    #Remote Methods ------------------------------------
    
    def waitForRun(self):
        self.callRemoteMethod("initEngines", None)
        return True;

        # TODO
        #if (self.raspberry):
        #    ret = self.CallRemoteMethod("init", None, 3)
        #    if (ret == 'go;'):
        #        return True
        #    else:
        #        return False
        #else:
        #    return True

    def setSpeed(self, speed):
        args = [speed]
        return self.callRemoteMethod("setSpeed", args)
    
    def setDriveAngle(self, angle):

        if (angle == 0):
            print "STRAIGHT"
        else:
            if (angle < 0):
                cmd = self.CMD_LEFT_TURN
                print "LEFT"
            else:
                cmd = self.CMD_RIGHT_TURN
                print "RIGHT"
            
            return self.callRemoteMethod("driveCurve", [cmd])
        
    def isBatteryLow(self):
        if (self.raspberry):
            return self.callRemoteMethod("battery", None)
        else:
            return 0
        
    def openGrabber(self):
        return self.callRemoteMethod("openCloseGrabber", [1])
        
    def closeGrabber(self):
        return self.callRemoteMethod("openCloseGrabber", [0])
        
    def clearContainer(self):
        return self.callRemoteMethod("clearContainer", None)
    
    def getDistance(self):
        return self.callRemoteMethod("getDistance", None)
    
    def openThrough(self):
        return self.callRemoteMethod("openCloseThrough", [1])
    
    def closeThrough(self):
        return self.callRemoteMethod("openCloseThrough", [0])
        
    def setGrabberPosition(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def resetGrabberPosition(self):
        raise NotImplementedError( "Should have implemented this" )
    
    #communication
    def callRemoteMethod(self, method, array_args, debugInfo = False):
        command = Utilities.SerializeMethodWithParameters(method, array_args)
        
        if (debugInfo):
            print "Calling remote method on freedom board: " + command

        if (self.raspberry):
            self.serial.write(command)
            ret = ser.readline()
            if (ret and debugInfo):
                print "Freedom board returned: " + ret

            return Utilities.DeserializeMethodWithParameters(method, ret)
        else:
            return 1;
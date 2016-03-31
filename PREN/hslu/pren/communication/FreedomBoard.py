'''
Created on 08.12.2015

@author: Christoph
@todo: Methoden implementieren
@todo: import serial (Raspberry Pi only)
@todo: implement callRemoteMethod
'''

import hslu.pren.common.Utilities
import wave
from hslu.pren.common import Utilities
from _random import Random
#import serial


class FreedomBoardCommunicator():
    
    
    
    #Methods to call remotely
    SET_SPEED = "SetSpeed"
    SET_GRABBER_POSITION = "SetGrabberPosition"
    GET_DISTANCE = "GetDistance"

    CMD_LEFT_TURN = 1
    CMD_RIGHT_TURN = 2

    #Constructor
    def __init__(self, serialPortName="ttyUSB0", baudRate="9600", raspberry=False):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        self.raspberry = raspberry
    
    #Remote Methods
        
    def SetSpeed(self, speed):
        args = [speed]
        return self.CallRemoteMethod("SetSpeed", args, 11)
    
    def SetDriveAngle(self, angle):
        
        cmd = 0
            
        # wenn der angle kleiner als -5, dann setzen wir auf Linkskurve
        if (angle < 5):
            cmd = self.CMD_LEFT_TURN
            print "LEFT TURN"

        # wenn der angle groesser als 5, dann setzen wir auf Rechtskurve
        if (angle > 5):
            cmd = self.CMD_RIGHT_TURN
            print "RIGHT TURN"
            
        return self.CallRemoteMethod("SetCorrectionAngle", [cmd], 16)
        
    def SetGrabberPosition(self):
        return self.CallRemoteMethod("SetGrabberPosition", None, 21)
        
    def ResetGrabberPosition(self):
        return self.CallRemoteMethod("ResetGrabberPosition", None, 23)
        
    def OpenGrabber(self):
        args = [1]
        return self.CallRemoteMethod("OpenCloseGrabber", args, 19)
        
    def CloseGrabber(self):
        args = [0]
        return self.CallRemoteMethod("OpenCloseGrabber", args, 19)
        
    def ClearContainer(self):
        return self.CallRemoteMethod("ClearContainer", None, 17)
    
    def GetDistance(self):
        return self.CallRemoteMethod("GetDistance", None, 16)
    
    def OpenThrough(self):
        args = [1]
        return self.CallRemoteMethod("OpenCloseThrough", args, 19)
    
    def CloseThrough(self):
        args = [0]
        return self.CallRemoteMethod("OpenCloseThrough", args, 19)
    
    def WaitForRun(self):
        if (self.raspberry):
            return self.CallRemoteMethod("init", None, 3) == "go;"
        else:
            return True
    
    #communication
    def CallRemoteMethod(self, method, array_args, returnByteCount):
        print "Calling remote method '" + method + "' on freedom board"
        if (self.raspberry):
            ser = serial.Serial(self.serialPortName, self.baudRate)
        command = Utilities.SerializeMethodWithParameters(method, array_args)
        if (self.raspberry):
            ser.write(command)
            ret = ser.read(returnByteCount)
            return Utilities.DeserializeMethodWithParameters(method, ret)
        else:
            return 1;
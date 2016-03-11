'''
Created on 08.12.2015

@author: Christoph
@todo: Methoden implementieren
@todo: import serial (Raspberry Pi only)
@todo: implement callRemoteMethod
'''

import hslu.pren.common
#import serial


class FreedomBoardCommunicator():
    
    #Methods to call remotely
    SET_SPEED = "SetSpeed"
    SET_GRABBER_POSITION = "SetGrabberPosition"
    GET_DISTANCE = "GetDistance"
    
    #Constructor
    def __init__(self, serialPortName="ttyUSB0", baudRate="9600"):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
        
    
    #Remote Methods
        
    def SetSpeed(self, speed):
        args = [speed]
        self.CallRemoteMethod("SetSpeed", args, 11)
    
    def SetDriveAngle(self, angle):
        args = [angle]
        self.CallRemoteMethod("SetDriveAngle", args, 16)
        
    def SetGrabberPosition(self):
        self.CallRemoteMethod("SetGrabberPosition", None, 21)
        
    def ResetGrabberPosition(self):
        self.CallRemoteMethod("ResetGrabberPosition", None, 23)
        
    def OpenGrabber(self):
        args = [1]
        self.CallRemoteMethod("OpenCloseGrabber", args, 19)
        
    def CloseGrabber(self):
        args = [0]
        self.CallRemoteMethod("OpenCloseGrabber", args, 19)
        
    def ClearContainer(self):
        self.CallRemoteMethod("ClearContainer", None, 17)
    
    def GetDistance(self):
        self.CallRemoteMethod("GetDistance", None, 16)
    
    def OpenThrough(self):
        args = [1]
        self.CallRemoteMethod("OpenCloseThrough", args, 19)
    
    def CloseThrough(self):
        args = [0]
        self.CallRemoteMethod("OpenCloseThrough", args, 19)
    
    #communication
    def CallRemoteMethod(self, method, array_args, returnByteCount):
        #ser = serial.Serial(self.serialPortName, self.baudRate)
        #ser.write(serializeMethodWithParameters(method, array_args))
        #return ser.read(returnByteCount)
        raise NotImplementedError( "Should have implemented this" )
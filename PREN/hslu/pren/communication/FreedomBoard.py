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
        raise NotImplementedError( "Should have implemented this" )
    
    def SetDriveAngle(self, angle):
        raise NotImplementedError( "Should have implemented this" )
        
    def SetGrabberPosition(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def IncreaseGrabberDepth(self, depth):
        raise NotImplementedError( "Should have implemented this" )
        
    def ResetGrabberPosition(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def CloseGrabber(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def OpenGrabber(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def ClearContainer(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def ReturnContainer(self):
        raise NotImplementedError( "Should have implemented this" )
    
    def GetDistance(self):
        raise NotImplementedError( "Should have implemented this" )
    
    def OpenMulde(self):
        raise NotImplementedError( "Should have implemented this" )
    
    def CloseMulde(self):
        raise NotImplementedError( "Should have implemented this" )
    
    #communication
    def CallRemoteMethod(self):
        #ser = serial.Serial(self.serialPortName, self.baudRate)
        #ser.write(serializeMethodWithParameters())
        #return ser.read()
        raise NotImplementedError( "Should have implemented this" )
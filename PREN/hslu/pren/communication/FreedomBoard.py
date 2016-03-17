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
        return self.CallRemoteMethod("SetSpeed", args, 11)
    
    def SetDriveAngle(self, angle):
        
        # wenn der angle groesser als 15, dann setzen wir auf 15
        if (angle > 15):
            angle = 15
            
        # wenn der angle kleiner als -15, dann setzen wir auf -15
        if (angle < 15):
            angle = -15
        
        inverter = 1
        if (angle < 0):
            inverter = -1
            
        # Wir senden jeweils nur den Befehl fuer die Korrektur von [step] Grad
        step = 1
        actual = 0
        while (actual <= (angle * inverter)):
            actual = actual + step
            args = [(1 * inverter)]
            return self.CallRemoteMethod("SetDriveAngle", args, 16)
        
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
        #return ser.read(3) == "go;")
        
        return True
    
    #communication
    def CallRemoteMethod(self, method, array_args, returnByteCount):
        #ser = serial.Serial(self.serialPortName, self.baudRate)
        command = Utilities.SerializeMethodWithParameters(method, array_args)
        #ser.write(command)
        #ret = ser.read(returnByteCount)
        #return Utilities.DeserializeMethodWithParameters(method, ret)
        return 1;
        
        raise NotImplementedError( "Should have implemented this" )
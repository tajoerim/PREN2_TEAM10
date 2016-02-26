'''
Created on 08.12.2015

@author: Christoph

@todo: Methoden implementieren
@todo: import serial (Raspberry Pi only)
@todo: implement callRemoteMethod
'''

import hslu.pren.common

class SmartphoneCommunicator():
    
    #Class names to call remotely
    GET_CORRECTION_ANGLE = "GetCorrectionAngle"
    
    #Constructor
    def __init__(self, serialPortName="ttyUSB0", baudRate="9600"):
        self.serialPortName = serialPortName
        self.baudRate = baudRate
    
    def GetCorrectionAngle(self):
        raise NotImplementedError( "Should have implemented this" )
    
    #communication
    def CallRemoteMethod(self):
        #ser = serial.Serial(self.serialPortName, self.baudRate)
        #ser.write(serializeMethodWithParameters())
        #return ser.read()
        raise NotImplementedError( "Should have implemented this" )

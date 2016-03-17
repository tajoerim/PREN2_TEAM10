'''
Created on 04.03.2016

@author: Christoph
@todo: Methoden implementieren
'''

import hslu.pren.common
from random import randint

class Navigator():
    
    #Constructor
    def __init__(self, webcamPort):
        self.port = webcamPort
        
    def GetCorrectionAngle(self):
        
        return randint(1, 10)
        
        # SIEHE DIESE WEBSITE: http://roboticssamy.blogspot.ch/
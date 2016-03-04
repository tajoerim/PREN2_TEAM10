'''
Created on 04.03.2016

@author: Christoph
@todo: Methoden implementieren
'''

import hslu.pren.common


class Navigator():
    
    #Constructor
    def __init__(self, webcamPort):
        self.port = webcamPort
        
    def GetCorrectionAngle(self):
        
        # SIEHE DIESE WEBSITE: http://roboticssamy.blogspot.ch/
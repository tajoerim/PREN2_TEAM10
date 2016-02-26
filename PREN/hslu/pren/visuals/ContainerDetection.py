'''
Created on 08.12.2015

@author: Christoph

@todo: Implementiation
'''

class ContainerDetector():

    def __init__(self, color="blue"):
        self.color = color
        
    def CheckContainer(self):
        '''
        Prueft ob es sich bei dem gefunden Objekt um einen Container
        mit der gesuchten Farbe handelt
        '''
        
        raise NotImplementedError( "Should have implemented this" )    
    
    def CheckColor(self):
        '''
        Prueft ob der Container der richtigen Farbe entspricht
        '''
        
        raise NotImplementedError( "Should have implemented this" )
    
    def CheckContour(self):
        '''
        Prueft ob das Object der Form eines Containers entspricht
        '''
        
        raise NotImplementedError( "Should have implemented this" )
    
    def CheckPosition(self):
        '''
        Prueft ob sich der Container innerhalb des Greifers befindet
        
        Kleiner 0:    Zu weit links
        Grösser 0:    Zu weit rechts
        Gleich 0:    Mittig
        '''
        
        raise NotImplementedError( "Should have implemented this" )
    
    def CheckPositionDepth(self):
        '''
        Prueft ob sich der Container innerhalb des Greifers befindet
        
        Kleiner 0:         Zu weit weg
        Grösser gleich 0:  Positioniert
        '''
        
        raise NotImplementedError( "Should have implemented this" )
    
        
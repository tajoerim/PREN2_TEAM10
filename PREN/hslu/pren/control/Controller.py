'''
Created on 08.12.2015

@author: Christoph
'''

from hslu.pren.communication import FreedomBoard
from hslu.pren.track import TrackController
from hslu.pren.visuals import ContainerDetection
from hslu.pren.navigation import Navigator

import time

class Controller():
    
    #constant
    SPEED_STRAIGHT = 100
    SPEED_CURVE = 50
    SPEED_CROSSROAD = 50
    SPEED_DETECT = 25
    SPEED_POSITION_GRABBER = 5
    SPEED_STOP = 0
    
    INCREASE_GRABBER_DEPTH_VALUE = 5
    CONTAINER_TIMEOUT_VALUE = 100
    
    SEARCH_CONTAINER_COUNT = 2
    
    #Constructor
    def __init__(self, color, webcamPort, freedomPort, startPoint):
        self.color = color
        self.freedomPort = freedomPort
        self.webcamPort = webcamPort
        self.startPoint = startPoint
        
    def __str__(self): 
        return "Color: " + self.color + " | WebCam Port: " + self.webcamPort + " | Freedom Board Port: " + self.freedomPort + " | Start point: " + self.startPoint

    def run(self):
        '''
        Hauptcontrolling und das Herzstueck des Roboters
        Hier wird der gesamte Ablauf koordiniert und ausgewertet.
        '''
        
        running = True
        
        freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600)
        navigator = Navigator.Navigator(self.webcamPort)
        trackController = TrackController.TrackController(self.startPoint)
        containerDetecor = ContainerDetection.ContainerDetector(self.color)
        
        detectedContainers = 0
        waitTimeout = self.CONTAINER_TIMEOUT_VALUE # Ein Timer um sicherzustellen, dass die Container nicht zu oft geprueft werden

        while (freedom.WaitForRun() == False):
            time.sleep(2)

        while(running):
            
            # Spur erkennen
            angle = navigator.GetCorrectionAngle()
            freedom.SetDriveAngle(angle)
            
            # Position pruefen
            distance = freedom.GetDistance()
            location = trackController.GetPositionEvent(distance)
            
            if (location.action == 'checkContainer'):
            
                # Fahren / Container erkennen?
                freedom.SetSpeed(self.SPEED_STRAIGHT)
                
                waitTimeout = waitTimeout - 1 #Damit wir nicht staendig die Container pruefen
                
                # Noch mehr als ein Container uebrig?
                if (detectedContainers < self.SEARCH_CONTAINER_COUNT and waitTimeout < 1):
                    waitTimeout = self.CONTAINER_TIMEOUT_VALUE;
                    container = containerDetecor.CheckContainer(True, 100)
                    
                    # Objekt erkannt?
                    if (container is not None):
                    
                        freedom.SetSpeed(0)
                        
                        # Greifer positionieren
                        tryAgain = True
                        while tryAgain:
                            position = container.topCenter
                            
                            if (position == 0):
                                freedom.SetSpeed(0)
                                tryAgain = False
                                
                            elif (position < 0):
                                freedom.SetSpeed(5)
                                
                            elif (position > 0):
                                freedom.SetSpeed(-5)
                                
                            # Container neu erkennen um Position zu ermitteln
                            container = containerDetecor.CheckContainer() 
                                
                        while (containerDetecor.CheckPositionDepth() < 0):
                            freedom.IncreaseGrabberDepth(self.INCREASE_GRABBER_DEPTH_VALUE)
                        
                        freedom.CloseGrabber()      # Greifen
                        freedom.ClearContainer()    # Entleeren
                        freedom.ReturnContainer()   # Abstellen
                        
                        detectedContainers = detectedContainers + 1
                        
            else:
                waitTimeout = 0 # Container Check timout zuruecksetzen
                      
                if (location.action == 'driveCurve'):
                    
                    additionalInfo = location.addInfo
                    freedom.SetSpeed(self.SPEED_CURVE)
                    
                                  
                elif (location.action == 'crossingRoad'):
                    
                    additionalInfo = location.addInfo
                    freedom.SetSpeed(self.SPEED_CROSSROAD)
                    
                    raise NotImplementedError( "Should have implemented this" )
                    # Kreuzung?
                    
                        # Gegner erkannt?
                        
                            # Max 15 Sec. warten (ACHTUNG: NUR WENN TIMOUT NOCH NIE ABGEWARTET FUER DIESE KREUZUNG!!!)
                                        
                elif (location.action == 'initStart'):
                    
                    freedom.SetSpeed(self.SPEED_STRAIGHT)   # Geradeaus
                    time.sleep(2)                           # Dann zwei Sekunden fahren
                    freedom.SetDriveAngle(-15)              # Dann 15 Grad nach links
                    time.sleep(2)                           # Dann zwei Sekunden fahren
                    freedom.SetDriveAngle(15)               # Dann 15 Grad nach rechts
                    
                    freedom.SetSpeed(0)                     # Neu positionieren
                    angle = navigator.GetCorrectionAngle()
                    freedom.SetDriveAngle(angle)
                    freedom.SetSpeed(self.SPEED_STRAIGHT)   # Geradeaus
                    
                                        
                elif (location.action == 'initEnd'):
                    
                    freedom.SetSpeed(self.SPEED_STRAIGHT)
                    
                    raise NotImplementedError( "Should have implemented this" )
                    
                    # Ausfahrt...
                    
                    # Entleeren
                    freedom.OpenThrough()
                    time.sleep(2)           # Dann zwei Sekunden warten
                    freedom.CloseThrough()
                        
                    
                    running = False # Fertig :)
                            
                    
            
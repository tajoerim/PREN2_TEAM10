'''
Created on 08.12.2015

@author: Christoph
'''

from hslu.pren.communication import *
from hslu.pren.track import *

class Controller():
    
    #Constructor
    def __init__(self, color, smartphonePort, freedomPort, startPoint):
        self.color = color
        self.smartphonePort = smartphonePort
        self.freedomPort = freedomPort
        self.startPoint = startPoint
        
    def __str__(self): 
        return "Color: " + self.color + " | Smartphone Port: " + self.smartphonePort + " | Freedom Board Port: " + self.freedomPort + " | Start point: " + self.startPoint

    def run(self):
        '''
        Hauptcontrolling und das Herzstück des Roboters
        
        Hier wird der gesamte Ablauf koordiniert und ausgewertet.
        '''
        
        running = True
        
        freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600)
        smartphone = Smartphone.SmartphoneCommunicator(self.smartphonePort, 9600)
        trackController = TrackController.TrackController(self.startPoint)
        
        while(running):
            
            # Spur erkennen
            angle = freedom.GetCorrectionAngle()
            
            # Position pruefen
            distance = freedom.GetDistance()
            location = trackController.GetPositionEvent(distance)
            
            if (location.action == 'checkContainer'):
                
                raise NotImplementedError( "Should have implemented this" )
            
                # Fahren / Container erkennen?
                
                    # Noch mehr als ein Container uebrig?
                
                        # Objekt erkannt? 
                            
                            # Objekt Form korrekt?
                            
                                # Objekt Farbe korrekt?
                                
                                    # Greifer positionieren
                                    
                                    # Greifen
                                    
                                    # Entleeren
                                    
                                    # Abstellen
                      
            elif (location.action == 'driveCurve'):
                
                additionalInfo = location.addInfo
                
                raise NotImplementedError( "Should have implemented this" )
                
                              
            elif (location.action == 'crossingRoad'):
                
                additionalInfo = location.addInfo
                
                raise NotImplementedError( "Should have implemented this" )
                # Kreuzung?
                
                    # Gegner erkannt?
                    
                        # Max 15 Sec. warten (ACHTUNG: NUR WENN TIMOUT NOCH NIE ABGEWARTET FUER DIESE KREUZUNG!!!)
                                    
            elif (location.action == 'initStart'):
                
                raise NotImplementedError( "Should have implemented this" )
                
                # Einfahrt?
                
                    # Gewisse Linien filtern
                                    
            elif (location.action == 'initEnd'):
                
                raise NotImplementedError( "Should have implemented this" )
                
                # Ausfahrt?
                
                    # Gewisse Linien filtern
                
                # Entladen?
                
                    # Klappe oeffnen
                    
                    # Warten bis leer
                    
                    # Klappe schliessen
                    
                # Fertig :)
                running = False
                            
                    
            
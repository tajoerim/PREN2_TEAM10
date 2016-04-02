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
    SPEED_STRAIGHT = 1000
    SPEED_CURVE = 500
    SPEED_CROSSROAD = 200
    SPEED_DETECT = 400
    SPEED_POSITION_GRABBER = 200
    SPEED_STOP = 0 # BEI STOP IMMER DEN NavigatorComm auf waiting setzen!
    
    INCREASE_GRABBER_DEPTH_VALUE = 5
    CONTAINER_TIMEOUT_VALUE = 100
    
    SEARCH_CONTAINER_COUNT = 2
    
    #Constructor
    def __init__(self, color, webcamPort, freedomPort, startPoint, raspberry, debug):
        self.color = color
        self.freedomPort = freedomPort
        self.webcamPort = webcamPort
        self.startPoint = startPoint
        self.raspberry = raspberry
        self.debug = debug
        print "Color: " + self.color + " | WebCam Port: " + self.webcamPort + " | FreedomBoard Port: " + self.freedomPort

    def run(self):
        '''
        Hauptcontrolling und das Herzstueck des Roboters
        Hier wird der gesamte Ablauf koordiniert und ausgewertet.
        '''
        
        self.running = True
        
        print "Initialize components"
        self.freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600, self.raspberry)
        self.trackController = TrackController.TrackController(self.startPoint)
        self.containerDetecor = ContainerDetection.ContainerDetector(self.color, self.debug)
        self.navigatorAgent = Navigator.NavigatorAgent(self.freedom, self.webcamPort, self.debug)
        print "Components initialized"

        self.detectedContainers = 0
        self.containerWaitTimeout = self.CONTAINER_TIMEOUT_VALUE # Ein Timer um sicherzustellen, dass die Container nicht zu oft geprueft werden

        print "Initialize Freedomboard"
        while (self.freedom.waitForRun() == False):
            time.sleep(2)
        print "Freedomboard initialized"

        print "Initialize navigatorAgent"
        self.navigatorAgent.start()
        print "navigatorAgent initialized"

        print "Initialize containerDetecor"
        #self.containerDetecor.start()
        print "containerDetecor initialized"

        while(self.running):
            
            self.checkBattery()
            time.sleep(1)
            location = self.checkPosition()
            
            if (location.action == 'checkContainer' and detectedContainers < self.SEARCH_CONTAINER_COUNT):
            
                self.actionContainer()

            else:
                self.containerWaitTimeout = 0 # Container Check timout zuruecksetzen (0 damit wir beim naechsten Container event gleich pruefen)
                      
                if (location.action == 'driveCurve'):
                    
                    additionalInfo = location.addInfo
                    self.freedom.setSpeed(self.SPEED_CURVE)
                                  
                elif (location.action == 'crossingRoad'):
                    
                    additionalInfo = location.addInfo
                    self.freedom.setSpeed(self.SPEED_CROSSROAD)
                    
                    raise NotImplementedError( "Should have implemented this" )
                    # Kreuzung?
                    
                        # Gegner erkannt?
                        
                            # Max 15 Sec. warten (ACHTUNG: NUR WENN TIMOUT NOCH NIE ABGEWARTET FUER DIESE KREUZUNG!!!)
                                        
                elif (location.action == 'initStart'):
                    
                    raise NotImplementedError( "Should have implemented this" )
                    
                                        
                elif (location.action == 'initEnd'):
                    
                    self.freedom.setSpeed(self.SPEED_STRAIGHT)
                    
                    raise NotImplementedError( "Should have implemented this" )
                    
                    # Ausfahrt...
                    
                    # Entleeren
                    self.freedom.setSpeed(self.SPEED_STOP)
                    self.navigatorAgent.waiting = True
                    self.freedom.openThrough()
                    time.sleep(2)           # Dann zwei Sekunden warten
                    self.freedom.closeThrough()
                        
                    self.stop()

                else: #normale Fahrt, ohne Container (alle abbgeraeumt)
                    self.freedom.setSpeed(SPEED_STRAIGHT)

    def checkBattery(self):
        if (self.freedom.isBatteryLow()):
            self.stop()

            while (True):
                print "[WARNING]: BATTERY LOW!"
                time.sleep(1)

    def checkPosition(self):
        distance = self.freedom.getDistance()
        #location = trackController.GetPositionEvent(distance)
        return self.trackController.getPositionEvent(450)

    def stop(self):
        
        print "STOPPING"

        #stoppen
        running = False

        #aufraeumen
        self.freedom.setSpeed(self.SPEED_STOP)
        if (self.raspberry):
            self.freedom.serial.close()

        self.navigatorAgent.running = False
        self.containerDetecor.running = False
        
        time.sleep(1)
        print ""
        print ""
        print ""
        print "GOOD BYE... :'("
        time.sleep(3)

    def actionContainer(self):
        self.freedom.setSpeed(self.SPEED_DETECT)

        self.containerWaitTimeout = self.containerWaitTimeout - 1 #Damit wir nicht staendig die Container pruefen
                
        # Noch mehr als ein Container uebrig?
        if (self.containerWaitTimeout < 1):
                    
            self.containerWaitTimeout = self.CONTAINER_TIMEOUT_VALUE;
                    
            # Objekt erkannt?
            if (self.containerDetecor.GetContainer()):
                    
                self.freedom.setSpeed(self.SPEED_STOP)
                self.navigatorAgent.waiting = True
                        
                # Greifer positionieren
                tryAgain = True
                while tryAgain:
                                
                    # Container neu erkennen um Position zu ermitteln
                    container = self.containerDetecor.CheckContainer() 
                    position = container.topCenter
                            
                    if (position == 0):
                        self.freedom.setSpeed(self.SPEED_STOP)
                        tryAgain = False
                                
                    elif (position < 0):
                        self.freedom.setSpeed(self.SPEED_POSITION_GRABBER)
                                
                    elif (position > 0):
                        self.freedom.setSpeed(self.SPEED_POSITION_GRABBER * -1)
                                
                while (containerDetecor.CheckPositionDepth() < 0):
                    self.freedom.IncreaseGrabberDepth(self.INCREASE_GRABBER_DEPTH_VALUE)
                        
                self.freedom.closeGrabber()      # Greifen
                self.freedom.clearContainer()    # Entleeren
                self.freedom.returnContainer()   # Abstellen
                        
                self.detectedContainers = self.detectedContainers + 1
                        
                self.navigatorAgent.waiting = False

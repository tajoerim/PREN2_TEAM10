'''
Created on 08.12.2015

@author: Christoph
'''

from hslu.pren.communication import FreedomBoard
from hslu.pren.track import TrackController
from hslu.pren.visuals import ContainerDetection
from hslu.pren.navigation import Navigator
from hslu.pren.control import BatteryAgent
from hslu.pren.control import ControllerGUI

import time
import cv2
import sys

class Controller():
    
    #constant
    SPEED_STRAIGHT = 3000
    SPEED_CURVE = 5000
    SPEED_CROSSROAD = 7000
    SPEED_DETECT = 7000
    SPEED_POSITION_GRABBER = 7000
    SPEED_STOP = 0 # BEI STOP IMMER DEN NavigatorComm auf waiting setzen!
    
    INCREASE_GRABBER_DEPTH_VALUE = 1
    CONTAINER_TIMEOUT_VALUE = 100
    
    SEARCH_CONTAINER_COUNT = 2
    
    #Constructor
    def __init__(self, color, webcamPort, freedomPort, startPoint, raspberry, debug, xVision):
        self.color = color
        self.freedomPort = freedomPort
        self.webcamPort = webcamPort
        self.startPoint = startPoint
        self.raspberry = raspberry
        self.debug = debug
        self.xVision = xVision
        print "Color: " + self.color + " | WebCam Port: " + self.webcamPort + " | FreedomBoard Port: " + self.freedomPort


    def run(self):

        try:
            self.printHeader()
            time.sleep(1)

            speedInput = raw_input("Set initial Speed :")
            if (speedInput is None or speedInput == ""):
                speedInput = str(self.SPEED_CURVE)

            if (self.debug and self.raspberry):
                print "Waiting for Visual Studio for attaching to process"
                input = raw_input("Press any key if you are ready...")
                print "Let's go!"

            '''
            Hauptcontrolling und das Herzstueck des Roboters
            Hier wird der gesamte Ablauf koordiniert und ausgewertet.
            '''
        
            self.running = True
        
            print "Initialize components"
            self.freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600, self.raspberry)
            self.trackController = TrackController.TrackController(self.startPoint)
            self.containerDetecor = ContainerDetection.ContainerDetector(self.color, self.xVision)
            self.navigatorAgent = Navigator.NavigatorAgent(self.freedom, self.raspberry, self.debug)
            self.batteryAgent = BatteryAgent.BatteryAgent(self.freedom, self.debug)

            print "Components initialized"

            self.detectedContainers = 0
            self.containerWaitTimeout = self.CONTAINER_TIMEOUT_VALUE # Ein Timer um sicherzustellen, dass die Container nicht zu oft geprueft werden

            print "Initialize navigatorAgent"
            self.navigatorAgent.start()
            print "navigatorAgent initialized"

            time.sleep(10)

            print "Initialize Freedomboard"
            while (self.freedom.waitForRun() == False):
                time.sleep(2)
            print "Freedomboard initialized"

            print "Initialize batteryAgent"
            self.batteryAgent.start()
            print "batteryAgent initialized"

            print "Initialize containerDetecor"
            #self.containerDetecor.start()
            print "containerDetecor initialized"

            while(self.running):
                
                time.sleep(1)

                self.checkBattery()
                location = self.checkPosition()
            
                if (location.action == 'checkContainer' and self.detectedContainers < self.SEARCH_CONTAINER_COUNT):
            
                    self.actionContainer()

                else:
                    self.containerWaitTimeout = 0 # Container Check timout zuruecksetzen (0 damit wir beim naechsten Container event gleich pruefen)
                      
                    if (location.action == 'driveCurve'):
                    
                        additionalInfo = location.addInfo
                        self.freedom.setSpeed(int(speedInput))
                                  
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
                    
                        if (self.navigatorAgent.getManualSpeed() == False):
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
                        self.freedom.setSpeed(self.SPEED_STRAIGHT)

        except KeyboardInterrupt:
            self.stop()

    def printHeader(self):
        print "########################################"
        print "#                                      #"
        print "# Software by:                         #"
        print "#                                      #"
        print "#     Christoph Joerimann              #"
        print "#     Matthias Kafka                   #"
        print "#                                      #"
        print "# Electronics by:                      #"
        print "#                                      #"
        print "#     Fabian Niderberger               #"
        print "#     Daniel Klauser                   #"
        print "#                                      #"
        print "# Robotics by:                         #"
        print "#                                      #"
        print "#     Simon Bernet                     #"
        print "#     David Andenmatten                #"
        print "#     Christoph Wittwer                #"
        print "#                                      #"
        print "# For TEAM 10 only                     #"
        print "#                                      #"
        print "# Hochschule Luzern                    #"
        print "# Technik & Architektur                #"
        print "#                                      #"
        print "# PREN 2 - FS16                        #"
        print "#                                      #"
        print "########################################" 
        print "#                                      #"
        print "#         GOOD LUCK TEAM 10            #"
        print "#                                      #"
        print "########################################" 

    def checkBattery(self):
        print "check Battery"
        if (self.batteryAgent.isBatteryLow()):
            self.stop()

            while (True):
                print "[WARNING]: BATTERY LOW!"
                time.sleep(1)
        print "Battery checked"

    def checkPosition(self):
        distance = self.freedom.getDistance()
        distance = 15800
        return self.trackController.getPositionEvent(distance)

    def stop(self):
       
        self.freedom.stop()

        print "STOPPING"

        #aufraeumen
        self.freedom.setSpeed(self.SPEED_STOP)
        if (self.raspberry):
            self.freedom.serial.close()
            
        self.running = False
        self.navigatorAgent.running = False
        self.containerDetecor.running = False
        self.batteryAgent.running = False
        
        time.sleep(1)
        print ""
        print ""
        print ""
        print "GOOD BYE... :'("
        time.sleep(1)

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

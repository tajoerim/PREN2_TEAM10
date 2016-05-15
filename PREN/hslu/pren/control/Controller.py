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
    SPEED_STRAIGHT = 4000
    SPEED_CURVE = 5000
    SPEED_CROSSROAD = 7000
    SPEED_DETECT = 15000
    SPEED_POSITION_GRABBER = 15000
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
        print "[CTRL] Color: " + self.color + " | WebCam Port: " + self.webcamPort + " | FreedomBoard Port: " + self.freedomPort


    def run(self):

        try:
            self.printHeader()
            time.sleep(1)

            speedInput = raw_input("Set initial Speed :")
            if (speedInput is None or speedInput == ""):
                speedInput = str(self.SPEED_CURVE)

            if (self.debug and self.raspberry):
                print "[CTRL] Waiting for Visual Studio for attaching to process"
                input = raw_input("Press any key if you are ready...")
                print "[CTRL] Let's go!"

            '''
            Hauptcontrolling und das Herzstueck des Roboters
            Hier wird der gesamte Ablauf koordiniert und ausgewertet.
            '''
        
            self.running = True
        
            print "[CTRL] Initialize components"
            self.freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600, self.raspberry)
            self.trackController = TrackController.TrackController(self.startPoint)
            self.containerDetecor = ContainerDetection.ContainerDetector(self.color, self.xVision, self.raspberry)
            self.navigatorAgent = Navigator.NavigatorAgent(self.freedom, self.raspberry, self.debug)
            self.batteryAgent = BatteryAgent.BatteryAgent(self.freedom, self.raspberry)

            print "[CTRL] Components initialized"

            self.detectedContainers = 0
            self.containerWaitTimeout = self.CONTAINER_TIMEOUT_VALUE # Ein Timer um sicherzustellen, dass die Container nicht zu oft geprueft werden

            print "[CTRL] Initialize navigatorAgent"
            self.navigatorAgent.start()
            print "[CTRL] navigatorAgent initialized"

            #while (self.freedom.getColor() == False):
                #time.sleep(2)

            print "[CTRL] Initialize batteryAgent"
            self.batteryAgent.start()
            print "[CTRL] batteryAgent initialized"

            print "[CTRL] Initialize containerDetecor"
            #self.containerDetecor.start()
            print "[CTRL] containerDetecor initialized"
            
            time.sleep(5)

            print "[CTRL] Initialize Freedomboard"
            self.freedom.initEngines(int(speedInput))
            print "[CTRL] Freedomboard initialized"

            while(self.running):
                
                time.sleep(1)

                self.checkBattery()
                location = self.checkPosition()
                if (location is not None):
                    print "[CTRL] LOCATION: " + location
            
                if (location is not None and location == 'checkContainer' and self.detectedContainers < self.SEARCH_CONTAINER_COUNT):
            
                    self.freedom.setLedColor(True, False, False);

                    self.actionContainer()

                else:
                    self.containerWaitTimeout = 0 # Container Check timout zuruecksetzen (0 damit wir beim naechsten Container event gleich pruefen)
                      
                    if (location is not None and location == 'driveCurve'):
                    
                        self.freedom.setLedColor(True, True, True);

                        additionalInfo = location.addInfo
                        self.freedom.setSpeed(int(speedInput))
                                  
                    elif (location is not None and location == 'crossingRoad'):
                    
                        self.freedom.setLedColor(True, True, False);
                    
                        additionalInfo = location.addInfo

                        self.freedom.setSpeed(self.SPEED_CROSSROAD)

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
        print "[CTRL] check Battery"
        if (self.batteryAgent.isBatteryLow()):
            self.stop()

            while (True):
                print "[CTRL] [WARNING]: BATTERY LOW!"
                time.sleep(1)
        print "[CTRL] Battery checked"

    def checkPosition(self):
        try:
            distance = self.freedom.getDistance();

            print "[CTRL] DISTANCE: " + str(distance)
            return self.trackController.getPositionEvent(distance)

        except:
            return None

    def stop(self):
       
        self.freedom.stop()

        print "[CTRL] STOPPING"

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
        print "[CTRL] GOOD BYE... :'("
        time.sleep(1)

    def actionContainer(self):
        self.freedom.setSpeed(self.SPEED_DETECT)

        self.containerWaitTimeout = self.containerWaitTimeout - 1 #Damit wir nicht staendig die Container pruefen
                
        # Noch mehr als ein Container uebrig?
        if (self.containerWaitTimeout < 1):
                    
            self.containerWaitTimeout = self.CONTAINER_TIMEOUT_VALUE;
                    
            # Objekt erkannt?
            if (self.containerDetecor.GetContainer() is not None):
                    
                freedom.stop();
                freedom.initEngines(15000);

                # Greifer positionieren
                tryAgain = True
                while tryAgain:
                    time.sleep(0.1)           
                    # Container neu erkennen um Position zu ermitteln
                    container = containerDetecor.GetContainer();
                    if (container is not None):
                        position = container.relativeCenter
                                
                        if (position < -20):
                            print "[CTRL] zu weit vorne" + str(position)
                                
                        elif (position > 20):
                            print "[CTRL] zu weit hinten" + str(position)
                            
                        else:
                            print "[CTRL] positioniert!!!"
                            tryAgain = False
                            
                freedom.stop();  
                  
                self.freedom.setLedColor(False, True, False)
                
                print "[CTRL] Flaeche" + str(container.GetFlaeche())

                while (container.GetFlaeche() < 25000):
                    print "[CTRL] zu weit weg" + str(container.GetFlaeche())
                    freedom.setGrabberPosition(2,0)
                    container = containerDetecor.GetContainer();
                    time.sleep(0.1)
                  
                self.freedom.setLedColor(True, True, False)
                    
                freedom.stop();
                print "[CTRL] ok"
                time.sleep(0.2)
                freedom.closeGrabber();
                time.sleep(5)
                freedom.openGrabber();

                containerDetecor.running = False;

                freedom.stop();
                  
                self.freedom.setLedColor(False, False, False)

                
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                        
                self.detectedContainers = self.detectedContainers + 1
                        
                self.navigatorAgent.waiting = False

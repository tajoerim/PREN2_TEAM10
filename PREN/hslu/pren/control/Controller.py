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
from hslu.pren.common import Logger

import time
import cv2
import sys

class Controller():
    
    #constant
    SPEED_STRAIGHT = 4000
    SPEED_CURVE = 5000
    SPEED_CROSSROAD = 7000
    SPEED_DETECT = 10000
    SPEED_POSITION_GRABBER = 20000
    
    CONTAINER_FLAECHE = 25000
    
    SEARCH_CONTAINER_COUNT = 2
    
    #Constructors
    def __init__(self, color, webcamPort, freedomPort, startPoint, raspberry, debug, xVision):
        self.color = color
        self.freedomPort = freedomPort
        self.webcamPort = webcamPort
        self.startPoint = startPoint
        self.raspberry = raspberry
        self.debug = debug
        self.xVision = xVision
        self.logger = Logger.Logger("CTRL")
        self.running = True
        # print"[CTRL] Color: " + self.color + " | WebCam Port: " + self.webcamPort + " | FreedomBoard Port: " + self.freedomPort


    def run(self):
        

        try:
            self.printHeader()
        
            showAsciiTrack = raw_input("Show ASCII Track? (N/y)");
            if (showAsciiTrack is None or showAsciiTrack == "n"):
                showAsciiTrack = False
            elif (showAsciiTrack == "y"):
                showAsciiTrack = True

            self.freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600, self.raspberry, showAsciiTrack)
            self.logger.log("waiting for color...", self.logger.HEADER)
            self.colorIdx = self.freedom.getColor()
            #self.colorIdx = "1"
            if (self.colorIdx == "1"):

                self.logger.log("  _____ _____ _____ _____ _____  ", self.logger.OKGREEN)
                self.logger.log(" |   __| __  |   __|   __|   | | ", self.logger.OKGREEN)
                self.logger.log(" |  |  |    -|   __|   __| | | | ", self.logger.OKGREEN)
                self.logger.log(" |_____|__|__|_____|_____|_|___| ", self.logger.OKGREEN)
                self.logger.log("                                 ", self.logger.OKGREEN)

            else:

                self.logger.log("  _____ __    _____ _____  ", self.logger.OKBLUE)
                self.logger.log(" | __  |  |  |  |  |   __| ", self.logger.OKBLUE)
                self.logger.log(" | __ -|  |__|  |  |   __| ", self.logger.OKBLUE)
                self.logger.log(" |_____|_____|_____|_____| ", self.logger.OKBLUE)
                self.logger.log("                           ", self.logger.OKBLUE)

            self.logger.log("Initialize components", self.logger.HEADER)
            self.trackController = TrackController.TrackController(self.startPoint)
            self.containerDetecor = ContainerDetection.ContainerDetector(self.colorIdx, False, self.raspberry)
            self.navigatorAgent = Navigator.NavigatorAgent(self.freedom, self.raspberry, True)
            self.batteryAgent = BatteryAgent.BatteryAgent(self.freedom, self.raspberry)
            self.logger.log("Components initialized", self.logger.HEADER)

            self.detectedContainers = 0
            
            self.logger.log("Initialize navigatorAgent", self.logger.HEADER)
            self.navigatorAgent.start()
            self.logger.log("navigatorAgent initialized", self.logger.HEADER)

            self.freedom.stop();
                
            self.logger.log("Initialize batteryAgent", self.logger.HEADER)
            self.batteryAgent.start()
            self.logger.log("batteryAgent initialized", self.logger.HEADER)
            
            self.logger.log("Initialize containerDetecor", self.logger.HEADER)
            self.containerDetecor.start()
            self.logger.log("containerDetecor initialized", self.logger.HEADER)
            
            time.sleep(5)
            
            self.logger.log("Initialize Freedomboard", self.logger.HEADER)
            self.freedom.initEngines(self.SPEED_STRAIGHT)
            self.logger.log("Freedomboard initialized", self.logger.HEADER)

            self.lastLocation = None

            while(self.running):
                
                time.sleep(0.5)

                self.checkBattery()

                location = self.checkPosition()

                #self.logger.log("LOCATION: " + location, self.logger.HEADER)
            
                if (location is not None and location == 'checkContainer' and self.detectedContainers < self.SEARCH_CONTAINER_COUNT):
            
                    if (self.lastLocation is None or self.lastLocation != location):
                        self.lastLocation = location

                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@ CHECK CONTAINER @@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);

                    self.freedom.setLedRed()
                    self.actionContainer()

                elif (location is not None and location == 'driveCurve'):
            
                    if (self.lastLocation is None or self.lastLocation != location):
                        self.lastLocation = location

                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@   DRIVE CURVE   @@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);
                        
                        self.freedom.setLedCyan()
                        self.freedom.setSpeed(self.SPEED_CURVE)
                    
                                  
                elif (location is not None and location == 'crossingRoad'):
            
                    if (self.lastLocation is None or self.lastLocation != location):
                        self.lastLocation = location

                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@    CROSSROAD    @@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);
                    
                        self.freedom.setLedYellow()
                        self.freedom.setSpeed(self.SPEED_CROSSROAD)

                        # wir warten max. 15 sec
                        cnt = 0
                        while (self.freedom.getDistanceEnemy < 20 and cnt < 15):
                            self.freedom.stop()
                            time.sleep(1)
                            cnt += 1

                else:
            
                    if (self.lastLocation is None or self.lastLocation != location):
                        self.lastLocation = location

                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@ DRIVE STRAIGHT  @@@@@@@@@@", self.logger.BOLD);
                        self.logger.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.logger.BOLD);

                        self.freedom.setLedWhite()
                        self.freedom.setSpeed(self.SPEED_STRAIGHT)

        except KeyboardInterrupt:
            self.stop()

    def printHeader(self):
        print"########################################"
        print"#                                      #"
        print"# Software by:                         #"
        print"#                                      #"
        print"#     Christoph Joerimann              #"
        print"#     Matthias Kafka                   #"
        print"#                                      #"
        print"# Electronics by:                      #"
        print"#                                      #"
        print"#     Fabian Niderberger               #"
        print"#     Daniel Klauser                   #"
        print"#                                      #"
        print"# Robotics by:                         #"
        print"#                                      #"
        print"#     Simon Bernet                     #"
        print"#     David Andenmatten                #"
        print"#     Christoph Wittwer                #"
        print"#                                      #"
        print"# For TEAM 10 only                     #"
        print"#                                      #"
        print"# Hochschule Luzern                    #"
        print"# Technik & Architektur                #"
        print"#                                      #"
        print"# PREN 2 - FS16                        #"
        print"#                                      #"
        print"########################################" 
        print"#                                      #"
        print"#         GOOD LUCK TEAM 10            #"
        print"#                                      #"
        print"########################################" 

    def checkBattery(self):
        if (self.batteryAgent.isBatteryLow()):
            self.stop()

            while (True):
                self.logger.log("BATTERY LOW", self.logger.WARNING)
                time.sleep(1)

    def checkPosition(self):
        try:
            distance = self.freedom.getDistance();
            
            if (distance == "go"):
                distance = None

            return self.trackController.getPositionEvent(distance)

        except:
            return None

    def stop(self):
       
        self.freedom.stop()
        
        self.logger.log("STOPPING", self.logger.HEADER)

        #aufraeumen
        self.freedom.stop()
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
        self.logger.log("GOOD BYE... :'(", self.logger.WARNING)
        time.sleep(1)

    def actionContainer(self):
        self.freedom.setSpeed(self.SPEED_DETECT)
          
        if (self.containerDetecor.GetContainer() is not None):
            
            self.freedom.setLedBlue()

            self.freedom.stop();
            self.freedom.initEngines(self.SPEED_POSITION_GRABBER);

            self.containerDetecor.wait = 1

            # Greifer positionieren
            tryAgain = True
            while tryAgain:
                time.sleep(0.1)           
                # Container neu erkennen um Position zu ermitteln
                container = self.containerDetecor.GetContainer();
                if (container is not None):
                    position = container.relativeCenter

                    color = self.logger.OKBLUE;
                    if (self.colorIdx == "1"):
                        color = self.logger.OKGREEN;

                    if (position < -20):
                        
                        self.logger.log("                                     ", color);
                        self.logger.log("                                     ", color);
                        self.logger.log("    _____________                    ", color);
                        self.logger.log("  ///////////////|                   ", color);
                        self.logger.log(" /////////////// |                   ", color);
                        self.logger.log("##############/ /|                   ", color);
                        self.logger.log(" ############/ / |                   ", color);
                        self.logger.log("##############/  |                   ", color);
                        self.logger.log("##############|  |                   ", color);
                        self.logger.log("##############|  |                   ", color);
                        self.logger.log("##############|  |                   ", color);
                        self.logger.log("##############|  /                   ", color);
                        self.logger.log("##############| /                    ", color);
                        self.logger.log("##############|/                     ", color);
                        self.logger.log(" ############/                       ", color);
                        self.logger.log("                                     ", self.logger.ENDC);
                        self.logger.log("                                     ", self.logger.ENDC);
                        self.logger.log("       ##                   ##       ", self.logger.ENDC);
                        self.logger.log("          ##             ##          ", self.logger.ENDC);
                        self.logger.log("             ##       ##             ", self.logger.ENDC);
                        self.logger.log("                ## ##                ", self.logger.ENDC);
                        self.logger.log("                                     ", self.logger.ENDC);
                        self.logger.log("                                     ", self.logger.ENDC);

                        self.logger.log("zu weit vorne: " + str(position), self.logger.HEADER)
                                
                    elif (position > 20):
                        
                        self.logger.log("                                         ", color);
                        self.logger.log("                                         ", color);
                        self.logger.log("                           _____________ ", color);
                        self.logger.log("                         ///////////////|", color);
                        self.logger.log("                        /////////////// |", color);
                        self.logger.log("                       ##############/ /|", color);
                        self.logger.log("                        ############/ / |", color);
                        self.logger.log("                       ##############/  |", color);
                        self.logger.log("                       ##############|  |", color);
                        self.logger.log("                       ##############|  |", color);
                        self.logger.log("                       ##############|  |", color);
                        self.logger.log("                       ##############|  /", color);
                        self.logger.log("                       ##############| / ", color);
                        self.logger.log("                       ##############|/  ", color);
                        self.logger.log("                        ############/    ", color);
                        self.logger.log("                                         ", color);
                        self.logger.log("                                         ", self.logger.ENDC);
                        self.logger.log("        ___                    ___       ", self.logger.ENDC);
                        self.logger.log("       /##/                   /##/       ", self.logger.ENDC);
                        self.logger.log("          /##/             /##/          ", self.logger.ENDC);
                        self.logger.log("             /##/       /##/             ", self.logger.ENDC);
                        self.logger.log("                /##/ /##/                ", self.logger.ENDC);
                        self.logger.log("                                         ", self.logger.ENDC);
                        self.logger.log("                                         ", self.logger.ENDC);

                        self.logger.log("zu weit hinten: " + str(position), self.logger.HEADER)
                            
                    else:
                        
                        self.logger.log("                                         ", color);
                        self.logger.log("                                         ", color);
                        self.logger.log("                 _____________           ", color);
                        self.logger.log("               ///////////////|          ", color);
                        self.logger.log("              /////////////// |          ", color);
                        self.logger.log("             ##############/ /|          ", color);
                        self.logger.log("              ############/ / |          ", color);
                        self.logger.log("             ##############/  |          ", color);
                        self.logger.log("             ##############|  |          ", color);
                        self.logger.log("             ##############|  |          ", color);
                        self.logger.log("             ##############|  |          ", color);
                        self.logger.log("             ##############|  /          ", color);
                        self.logger.log("             ##############| /           ", color);
                        self.logger.log("             ##############|/            ", color);
                        self.logger.log("              ############/              ", color);
                        self.logger.log("                                         ", color);
                        self.logger.log("                                         ", self.logger.ENDC);
                        self.logger.log("        ___                    ___       ", self.logger.ENDC);
                        self.logger.log("       /##/                   /##/       ", self.logger.ENDC);
                        self.logger.log("          /##/             /##/          ", self.logger.ENDC);
                        self.logger.log("             /##/       /##/             ", self.logger.ENDC);
                        self.logger.log("                /##/ /##/                ", self.logger.ENDC);
                        self.logger.log("                                         ", self.logger.ENDC);
                        self.logger.log("                                         ", self.logger.ENDC);

                        self.logger.log("positioniert", self.logger.HEADER)
                        tryAgain = False
                            
            self.freedom.closeGrabber();
                  
            self.freedom.setLedGreen()

            for x in range(0, 10):
                self.freedom.setGrabberPosition(0,2)
                
            for x in range(0, 5):
                self.freedom.setGrabberPosition(2,0)
                time.sleep(0.1)
                
            self.logger.log("Flaeche" + str(container.GetFlaeche()), self.logger.HEADER)

            self.freedom.openGrabber();

            while (container.GetFlaeche() < self.CONTAINER_FLAECHE):
                self.logger.log("zu weit weg" + str(container.GetFlaeche()), self.logger.HEADER)
                self.freedom.setGrabberPosition(2,0)
                container = None
                while (True):
                    container = self.containerDetecor.GetContainer();
                    if (container is not None):
                        break

                time.sleep(0.1)

            self.freedom.stop();
            self.freedom.closeGrabber();
            
            time.sleep(2)

            self.freedom.openGrabber();
            self.freedom.stop();

            for x in range(0, 20):
                self.freedom.setGrabberPosition(0,1)

            for x in range(0, 10):
                self.freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                        
            self.detectedContainers = self.detectedContainers + 1

            if (self.detectedContainers > 2):
                self.containerDetecor.running = False;
                
            self.freedom.initEngines();

            self.navigatorAgent.waiting = False
                  
            self.freedom.setLedOff()

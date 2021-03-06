﻿'''
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
import traceback

try:
    import pygame
    pygame.mixer.init()
except:
    print "SORRY NO SOUND"

class Controller():
    
    #constant
    SPEED_STRAIGHT = 5000
    SPEED_CURVE = 5000
    SPEED_CROSSROAD = 5000
    SPEED_DETECT = 5000
    SPEED_POSITION_GRABBER = 7000
    
    CONTAINER_FLAECHE = 22000
    
    SEARCH_CONTAINER_COUNT = 3
    
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
        self.checkLocation = False
        self.initialPositionValue = 0
        self.resetInitialLine = False
        self.lastContainerPosition = 0
        self.distance = 0

    def run(self):

        try:
            self.printHeader()

            showAsciiTrack = False
            #showAsciiTrack = raw_input("Show ASCII Track?  (N/y)");
            #if (showAsciiTrack is None or showAsciiTrack == "n"):
            #    showAsciiTrack = False
            #elif (showAsciiTrack == "y"):
            #    showAsciiTrack = True

            startPosition = raw_input("Start Position? (A/b)")
            if (startPosition is None):
                startPosition = "A"
            elif (startPosition == "b"):
                startPosition = "B"

            self.freedom = FreedomBoard.FreedomBoardCommunicator(self.freedomPort, 9600, self.raspberry, showAsciiTrack)
            self.logger.log("waiting for color...", self.logger.HEADER)
            self.colorIdx = self.freedom.getColor()
            #self.colorIdx = "1"

            self.freedom.setLedOff()

            print "\n\n"

            if (self.colorIdx == "1"):
                self.freedom.setLedGreen()
                self.logger.log("  _____ _____ _____ _____ _____  ", self.logger.OKGREEN, False)
                self.logger.log(" |   __| __  |   __|   __|   | | ", self.logger.OKGREEN, False)
                self.logger.log(" |  |  |    -|   __|   __| | | | ", self.logger.OKGREEN, False)
                self.logger.log(" |_____|__|__|_____|_____|_|___| ", self.logger.OKGREEN, False)
                self.logger.log("                                 ", self.logger.OKGREEN, False)

            else:
                self.freedom.setLedBlue()
                self.logger.log("  _____ __    __  __ _____  ", self.logger.OKBLUE, False)
                self.logger.log(" | __  |  |  |  ||  |   __| ", self.logger.OKBLUE, False)
                self.logger.log(" | __ -|  |__|  ||  |   __| ", self.logger.OKBLUE, False)
                self.logger.log(" |_____|_____|______|_____| ", self.logger.OKBLUE, False)
                self.logger.log("                            ", self.logger.OKBLUE, False)

            print "\n\n"
                
            sys.stdout.write("\n\rInitialize components")
            sys.stdout.flush()

            self.trackController = TrackController.TrackController(startPosition)
            self.containerDetecor = ContainerDetection.ContainerDetector(self.colorIdx, True, self.raspberry)
            self.navigatorAgent = Navigator.NavigatorAgent(self.freedom, self.raspberry, False)
            self.batteryAgent = BatteryAgent.BatteryAgent(self.freedom, self.raspberry)
            sys.stdout.write("\rInitialize components - \033[92m SUCCESS\033[0m")

            self.detectedContainers = 0
            
            sys.stdout.write("\n\rInitialize navigatorAgent")
            sys.stdout.flush()
            self.navigatorAgent.start()
            sys.stdout.write("\rInitialize navigatorAgent - \033[92m SUCCESS\033[0m")
            
            sys.stdout.write("\n\rReset grabber position")
            sys.stdout.flush()
            self.freedom.stop()
            self.freedom.openGrabber()
            self.freedom.setGrabberUpToEnd()
            self.freedom.setGrabberBackToEnd()
            self.freedom.stop()
            self.freedom.closeGrabber()
            self.freedom.stop()
            sys.stdout.write("\rReset grabber position - \033[92m SUCCESS\033[0m")
                
            sys.stdout.write("\n\rInitialize batteryAgent")
            sys.stdout.flush()
            self.batteryAgent.start()
            sys.stdout.write("\rInitialize batteryAgent - \033[92m SUCCESS\033[0m")
            
            sys.stdout.write("\n\rInitialize containerDetecor")
            sys.stdout.flush()
            self.containerDetecor.start()
            sys.stdout.write("\rInitialize containerDetecor - \033[92m SUCCESS\033[0m")

            time.sleep(2)
            self.freedom.initEngines(self.SPEED_STRAIGHT)

            print "\n\n"

            self.lastLocation = None
            location = None

            while(self.running):

                self.checkBattery()

                #if (self.checkLocation):
                location = self.checkPosition()

                if (location == "stop"):
                    self.freedom.stop()

                if (self.distance > 12100):
                    self.freedom.stop()
                    time.sleep(2)
                    self.freedom.unloadThrough()
                    self.running = False

                if (location is not None and location == 'checkContainer' and self.detectedContainers < self.SEARCH_CONTAINER_COUNT):

                    self.navigatorAgent.navigator.LINETOLLERANCE = 10000
                    self.navigatorAgent.navigator.ANGLE = 50
                    
                    if (self.containerDetecor.running):
                        if (self.lastLocation is None or self.lastLocation != location):
                            self.logger.log("CHECK CONTAINER", self.logger.OKBLUE, True)
                            self.lastLocation = location
                            self.freedom.setSpeed(self.SPEED_DETECT)
                            self.freedom.setLedYellow()

                        if ((self.distance - self.lastContainerPosition) > 100):
                            self.actionContainer()
                            self.lastContainerPosition = self.distance

                    time.sleep(1)

                elif (location is not None and location == 'driveCurve'):

                    self.navigatorAgent.navigator.LINETOLLERANCE = 10000
                    self.navigatorAgent.navigator.ANGLE = 50

                    if (self.lastLocation is None or self.lastLocation != location):
                        self.logger.log("DRIVE CURVE", self.logger.OKBLUE, True)
                        self.lastLocation = location
                        self.freedom.setSpeed(self.SPEED_CURVE)
                        self.freedom.setLedCyan()
                                  
                elif (location is not None and location == 'crossingRoad'):

                    if (self.lastLocation is None or self.lastLocation != location):
                        self.logger.log("CROSSROAD", self.logger.OKBLUE, True)
                        self.lastLocation = location
                        self.navigatorAgent.navigator.ANGLE = 50
                        self.freedom.setSpeed(self.SPEED_CROSSROAD)
                        self.freedom.setLedRed()

                    dist = self.freedom.getDistanceEnemy()

                    cnt = 0
                    while (dist > 0 and dist < 20 and cnt < 10):
                        self.navigatorAgent.waiting = True
                        self.freedom.stop()
                        time.sleep(1)
                        cnt += 1

                        dist = self.freedom.getDistanceEnemy()
                        if (dist > 20 or dist < 1):
                            self.navigatorAgent.waiting = False
                            self.freedom.initEngines()
                            break

                    self.navigatorAgent
                                  
                elif (location is not None and location == 'handlePitLane' and self.distance > 3000):
                    
                    if (self.lastLocation is None or self.lastLocation != location):
                        self.logger.log("PITLANE", self.logger.OKBLUE, True)
                        self.lastLocation = location
                        self.navigatorAgent.navigator.ANGLE = 40
                        self.navigatorAgent.navigator.LINETOLLERANCE = 7000
                        self.freedom.setLedWhite()

                    self.navigatorAgent.searchZiel()

                    if(self.navigatorAgent.isZielFound()):
                        time.sleep(1.5)
                        self.freedom.stop()
                        time.sleep(2)
                        self.freedom.unloadThrough()
                        self.running = False

                else:
            
                    if (self.lastLocation is None or self.lastLocation != location):
                        self.lastLocation = location
                        self.navigatorAgent.navigator.ANGLE = 30
                        self.navigatorAgent.navigator.LINETOLLERANCE = 6000
                        self.freedom.setLedWhite()
                        self.freedom.setSpeed(self.SPEED_STRAIGHT)

                    #self.checkLocation = True
                    #if (self.checkLocation == False):

                    #    self.checkLocation = self.navigatorAgent.isLineFound()
                    #    self.checkLocation = True
                    #    if (self.initialPositionValue == 0 and self.checkLocation == True):
                    #        self.initialPositionValue = int(self.freedom.getDistance())
        except:
            traceback.print_exc()
            print sys.exc_info()[0]
            self.stop()

    def printHeader(self):
        print"########################################"
        print"#                                      #"
        print"#           PREN 2 - FS16              #"
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
            distance = self.freedom.getDistance()
            
            if (distance is None or distance == "go" or distance == ''):
                return None

            distance = int(distance) - self.initialPositionValue
            self.distance = distance
            print str(self.distance)
            return self.trackController.getPositionEvent(str(distance))

        except:
            traceback.print_exc()
            print sys.exc_info()[0]
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

            self.freedom.stop()
            self.freedom.initEngines(self.SPEED_POSITION_GRABBER)

            self.containerDetecor.wait = 1

            # Greifer positionieren
            tryAgain = True
            while tryAgain:
                time.sleep(0.1)           
                # Container neu erkennen um Position zu ermitteln
                container = self.containerDetecor.GetContainer()
                if (container is not None):
                    position = container.relativeCenter

                    color = self.logger.OKBLUE
                    if (self.colorIdx == "1"):
                        color = self.logger.OKGREEN

                    if (position < -20):
                        self.logger.log("zu weit vorne: " + str(position), self.logger.HEADER)
                                
                    elif (position > 70):
                        self.endContainer()
                        return # hier ist es bereits zu spät
                            
                    else:
                        self.logger.log("positioniert", self.logger.HEADER)
                        tryAgain = False
               

            self.navigatorAgent.waiting = True

            self.freedom.stop()
            time.sleep(1)
            self.freedom.stop()

            self.freedom.openGrabber()
            self.freedom.stop()
            
            for x in range(0, 15):
                self.freedom.setGrabberPositionDown()
            
            self.freedom.setGrabberFrontToEnd()

            self.logger.log("ZUGRIFF", self.logger.WARNING)

            self.freedom.stop()
            time.sleep(1)
            self.freedom.closeGrabber()
            self.freedom.setGrabberUpToEnd()
            self.freedom.setGrabberBackToEnd()

            time.sleep(1)
            self.freedom.emptyContainer()
            time.sleep(1)

            self.freedom.dropContainer()

            self.endContainer()


    def endContainer(self):
            time.sleep(1)
            self.freedom.stop()

            self.logger.log("Container abschluss", self.logger.WARNING)
                        
            self.detectedContainers = self.detectedContainers + 1

            if (self.detectedContainers >= self.SEARCH_CONTAINER_COUNT):
                self.logger.log("Container Erkennung deaktivieren", self.logger.WARNING)
                self.containerDetecor.running = False

            time.sleep(1)
            self.freedom.initEngines()

            self.navigatorAgent.waiting = False
                  
            self.freedom.setLedOff()

            time.sleep(5)


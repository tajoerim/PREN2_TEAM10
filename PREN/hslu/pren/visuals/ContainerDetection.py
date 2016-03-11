'''
Created on 08.12.2015

@author: Christoph

@todo: Implementiation
'''

import cv2
import numpy as np
from imutils import contours
from hslu.pren.communication import *


class Container():
    def __init__(self, x, y, w, h):
        self.X1 = x
        self.Y1 = y
        self.X2 = x+w
        self.Y2 = y+h
        self.width = w
        self.height = h
        self.topCenter = ((x+w - x) / 2) + x
        
    def GetFlaeche(self):
        return self.width * self.height;
        

class ContainerDetector():

    def __init__(self, color="blue"):
        self.color = color
        
    def CheckContainer(self, debugWindow = False, loopCount = 1):
        '''
        Prueft ob es sich bei dem gefunden Objekt um einen Container
        mit der gesuchten Farbe handelt
        '''
        
        return self.GetPossibleContainer(debugWindow, loopCount)  
    
    def GetPossibleContainer(self, debugWindow = False, loopCount = 1):
        '''
        Sucht einen moeglichen Container und 
        prueft ob der Container der richtigen Farbe entspricht
        '''
        
        container = Container(0,0,0,0)
        
        #RASPBERRY PI
        #width = 320
        #height = 240
        
        #NOTEBOOK
        width = 640
        height = 480
        
        rangeX1 = 0
        rangeX2 = width
        rangeY1 = 20
        rangeY2 = 200
        
        rangeX3 = 200
        rangeX4 = 400
        rangeY3 = 0
        rangeY4 = height
        
        minFlaeche = 15000
            
        # initialize the camera and grab a reference to the raw camera capture
        cap = cv2.VideoCapture(0)

        counter = 0
        while(counter <= loopCount):
            counter = counter + 1
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Our operations on the frame come here
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            both = self.GetthresholdedimgBoth(hsv)
            erode = cv2.erode(both,None,iterations = 3)
            dilate = cv2.dilate(erode,None,iterations = 10)
        
            contours,hierarchy = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
            
            maxX = 0
            maxY = 0
            maxW = 0
            maxH = 0
            
            # Durch alle Konturen iterieren und nur die groesste im Range erfassen
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                
                if (y > rangeY1 and y < rangeY2 and x > rangeX1 and x < rangeX2):
                    if ((w*h > minFlaeche and w*h > maxW*maxH)):
                        maxX = x
                        maxY = y
                        maxH = h
                        maxW = w
            
            if (maxX > 0 and max > 0):
            
                container = Container(maxX, maxY, maxW, maxH)
                
                #cv2.rectangle(frame, (maxX,maxY), (maxX+maxW,maxY+maxH), (0,255,0), thickness=3, lineType=8, shift=0)
                cv2.rectangle(frame, (container.X1,container.Y1), (container.X2,container.Y2), (0,255,0), thickness=3, lineType=8, shift=0)
                cv2.circle(frame, (container.topCenter, container.Y1), 4, (0,0,255), -1)
                cv2.putText(frame, str(maxW*maxH), (maxX,maxY), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255),2)
                cv2.putText(frame, str(container.topCenter), (container.topCenter, container.Y1), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255),2)
                
            cv2.drawContours(frame, contours, -1, (255,0,0), 1)
            
            cv2.rectangle(frame, (rangeX1,rangeY1), (rangeX2,rangeY2), (255,0,0), thickness=1, lineType=8, shift=0)
            cv2.rectangle(frame, (rangeX3,rangeY3), (rangeX4,rangeY4), (255,0,0), thickness=1, lineType=8, shift=0)
            
            if debugWindow == True:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            counter = counter + 1
        
        # When everything done, release the capture
        cap.release()
        
        if debugWindow == True:
            cv2.destroyAllWindows()
        
        return container
    
    def CheckPositionDepth(self, container):
        '''
        Prueft ob sich der Container innerhalb des Greifers befindet
        
        Kleiner 0:         Zu weit weg
        Groesser gleich 0:  Positioniert
        '''
        
        #TODO: Wert fuer Flaeche finden
        return container.width > 200
    
    
    def GetthresholdedimgBlue(self, hsv):
        #blue = cv2.inRange(hsv,np.array((100,0,100)),np.array((120,255,255)))
        blue = cv2.inRange(hsv,np.array((100,20,80)),np.array((130,255,255)))
        return blue
    
    
    def GetthresholdedimgYellow(self, hsv):
        #yellow = cv2.inRange(hsv,np.array((0,115,84)),np.array((217,255,171)))
        yellow = cv2.inRange(hsv,np.array((20,90,80)),np.array((40,255,255)))
        return yellow
    
    
    def GetthresholdedimgBoth(self, hsv):
        both = cv2.add(self.GetthresholdedimgBlue(hsv),self.GetthresholdedimgYellow(hsv))
        return both
    
        
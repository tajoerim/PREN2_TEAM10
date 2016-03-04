'''
Created on 08.12.2015

@author: Christoph

@todo: Implementiation
'''

import cv2
import numpy as np
from imutils import contours

class ContainerDetector():

    def __init__(self, color="blue"):
        self.color = color
        
    def CheckContainer(self):
        '''
        Prueft ob es sich bei dem gefunden Objekt um einen Container
        mit der gesuchten Farbe handelt
        '''
        
        isColor = self.CheckColor()
        if (isColor == True):
            return self.CheckContour()
        
        raise NotImplementedError( "Should have implemented this" )    
    
    def CheckColor(self):
        '''
        Prueft ob der Container der richtigen Farbe entspricht
        '''
        
        width = 640
        height = 240
        
        rangeX1 = 0
        rangeX2 = width
        rangeY1 = 20
        rangeY2 = 200
        
        minFlaeche = 15000
            
        # initialize the camera and grab a reference to the raw camera capture
        cap = cv2.VideoCapture(0)
        
        while(True):
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
                    if (w*h > minFlaeche and w*h > maxW*maxH):
                        maxX = x
                        maxY = y
                        maxH = h
                        maxW = w
            
            cv2.rectangle(frame, (maxX,maxY), (maxX+maxW,maxY+maxH), (0,255,0), thickness=3, lineType=8, shift=0)
            cv2.putText(frame, str(maxW*maxH), (maxX,maxY), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255),2)
            
            cv2.drawContours(frame, contours, -1, (255,0,0), 1)
        
            cv2.rectangle(frame, (rangeX1,rangeY1), (rangeX2,rangeY2), (255,0,0), thickness=1, lineType=8, shift=0)
        
            # Display the resulting frame
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        
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
        Groesser 0:    Zu weit rechts
        Gleich 0:    Mittig
        '''
        
        raise NotImplementedError( "Should have implemented this" )
    
    def CheckPositionDepth(self):
        '''
        Prueft ob sich der Container innerhalb des Greifers befindet
        
        Kleiner 0:         Zu weit weg
        Groesser gleich 0:  Positioniert
        '''
        
        raise NotImplementedError( "Should have implemented this" )
    
    
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
    
        
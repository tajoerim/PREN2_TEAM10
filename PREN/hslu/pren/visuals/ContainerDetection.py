'''
Created on 08.12.2015

@author: Christoph

@todo: Implementiation
'''

import cv2
import numpy as np
from imutils import contours
import threading


class Container():
    def __init__(self, x, y, w, h):
        self.X1 = x
        self.Y1 = y
        self.X2 = x+w
        self.Y2 = y+h
        self.width = w
        self.height = h
        self.topCenter = ((x+w - x) / 2) + x
        self.relativeCenter = 0
        self.positioned = False
        
    def GetFlaeche(self):
        return self.width * self.height;
        

class ContainerDetector(threading.Thread):

    def __init__(self, color="2", port=0, xVision=False, raspberry=False):
        threading.Thread.__init__(self)
        self.color = color
        self.xVision = xVision
        self.container = None
        self.running = True
        self.port = port
        self.positioned = False
        self.raspberry = raspberry
        self.wait = 4
        
    def GetContainer(self):
        return self.container
    
    def nothing(*arg):
        pass

    def run(self):
        '''
        Sucht einen moeglichen Container und 
        prueft ob der Container der richtigen Farbe entspricht
        '''
        
        #RASPBERRY PI
        width = 320
        height = 240
        
        rangeX1 = 0
        rangeX2 = width
        rangeY1 = 70
        rangeY2 = height
        
        rangeX3 = 50
        rangeX4 = 200
        rangeY3 = 0
        rangeY4 = height
        
        rangeX5 = 25
        rangeX6 = 50
        rangeY5 = 0
        rangeY6 = height
        
        rangeX7 = 100
        rangeX8 = 175
        rangeY7 = 0
        rangeY8 = height
        
        minFlaeche = 4500
            
        # initialize the camera and grab a reference to the raw camera capture
        if (self.raspberry):
            cap = cv2.VideoCapture(self.port)
        else:
            cap = cv2.VideoCapture(0)

        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width); 
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height);

        while(self.running):

            # Capture frame-by-frame 
            ret, frame = cap.read()

            # Our operations on the frame come here
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            both = self.GetthresholdedimgBoth(hsv)
            erode = cv2.erode(both,None,iterations = 3)
            dilate = cv2.dilate(erode,None,iterations = 10)
        
            contours,hierarchy = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
            
            maxX = maxY = maxW = maxH = 0
            
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
                container.relativeCenter = container.topCenter - (width / 2)

                if self.raspberry == False:
                    cv2.putText(frame, str(maxW*maxH), (maxX,maxY), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255),2)
                    cv2.putText(frame, str(container.relativeCenter), (container.topCenter, container.Y1), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255),2)

                self.container = container

            else:

                self.container = None
            

            #if self.raspberry == False:
            #    cv2.drawContours(frame, contours, -1, (255,0,0), 1)
            #    cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): # Warten für x millisekunden
                break
        
        # When everything done, release the capture
        cap.release()
        
        if self.raspberry == False:
            cv2.destroyAllWindows()
    
    
    def GetthresholdedimgBlue(self, hsv):
        #blue = cv2.inRange(hsv,np.array((100,0,100)),np.array((120,255,255)))
        blue = cv2.inRange(hsv,np.array((106,6,34)),np.array((164,255,255)))
        return blue
    
    
    def GetthresholdedimgGreen(self, hsv):
        #yellow = cv2.inRange(hsv,np.array((0,115,84)),np.array((217,255,171)))
        green = cv2.inRange(hsv,np.array((50,0,0)),np.array((75,255,255)))
        return green
    
    
    def GetthresholdedimgBoth(self, hsv):
        if (self.color == "1"):
            return self.GetthresholdedimgGreen(hsv)
        elif (self.color == "2"):
            return self.GetthresholdedimgBlue(hsv)
        else:
            both = cv2.add(self.GetthresholdedimgBlue(hsv), self.GetthresholdedimgGreen(hsv))
            return both
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

    def __init__(self, color="blue", port=0, xVision=False, raspberry=False):
        threading.Thread.__init__(self)
        self.color = color
        self.xVision = xVision
        self.container = None
        self.running = True
        self.port = port
        self.positioned = False
        self.raspberry = raspberry
        
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
        width = 640 / 2
        height = 480 / 2
        
        rangeX1 = 0
        rangeX2 = width
        rangeY1 = 140 / 2
        rangeY2 = height
        
        rangeX3 = 100 / 2
        rangeX4 = 200 / 2
        rangeY3 = 0
        rangeY4 = height
        
        rangeX5 = 50 / 2
        rangeX6 = 100 / 2
        rangeY5 = 0
        rangeY6 = height
        
        rangeX7 = 200 / 2
        rangeX8 = 250 / 2
        rangeY7 = 0
        rangeY8 = height
        
        #minFlaeche = 20000
        minFlaeche = 7000 / 2
            
        # initialize the camera and grab a reference to the raw camera capture
        if (self.raspberry):
            cap = cv2.VideoCapture(self.port)
        else:
            cap = cv2.VideoCapture(0)

        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width); 
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height);

        if (self.raspberry == False):
            cv2.namedWindow('frame')
            cv2.createTrackbar('TOP1', 'frame', rangeY1, height, self.nothing)
            cv2.createTrackbar('TOP2', 'frame', rangeY2, height, self.nothing)
            cv2.createTrackbar('LEFT', 'frame', 140, width - 50, self.nothing)
            cv2.createTrackbar('RIGHT', 'frame', 515, width - 50, self.nothing)

        while(self.running):

            if (self.raspberry == False):
                rangeY1 = cv2.getTrackbarPos('TOP1', 'frame')
                rangeY2 = cv2.getTrackbarPos('TOP2', 'frame')
                
                left = cv2.getTrackbarPos('LEFT', 'frame')
                right = cv2.getTrackbarPos('RIGHT', 'frame')

                rangeX5 = left - 50
                rangeX6 = rangeX3 = left
                rangeX4 = rangeX7 = right
                rangeX8 = right + 50

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

                #cv2.rectangle(frame, (maxX,maxY), (maxX+maxW,maxY+maxH), (0,255,0), thickness=3, lineType=8, shift=0)
                #if (container.X1 < rangeX6 and container.X2 > rangeX7):
                #    cv2.rectangle(frame, (container.X1,container.Y1), (container.X2,container.Y2), (0,255,0), thickness=3, lineType=8, shift=0)
                #    container.positioned = True
                #else:
                #    cv2.rectangle(frame, (container.X1,container.Y1), (container.X2,container.Y2), (0,255,255), thickness=3, lineType=8, shift=0)

                #cv2.circle(frame, (container.topCenter, container.Y1), 4, (0,0,255), -1)
                #cv2.circle(frame, (container.X1, container.Y1), 4, (0,255,255), -1)
                #cv2.circle(frame, (container.X2, container.Y1), 4, (0,255,255), -1)
                #cv2.putText(frame, str(maxW*maxH), (maxX,maxY), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255),2)
                #cv2.putText(frame, str(container.relativeCenter), (container.topCenter, container.Y1), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255),2)

                self.container = container

            else:

                self.container = None
                
            #cv2.drawContours(frame, contours, -1, (255,0,0), 1)
            
            #cv2.rectangle(frame, (rangeX1,rangeY1), (rangeX2,rangeY2), (255,0,0), thickness=2, lineType=8, shift=0)
            #cv2.rectangle(frame, (rangeX3,rangeY3), (rangeX4,rangeY4), (255,0,0), thickness=2, lineType=8, shift=0)

            #cv2.rectangle(frame, (rangeX5,rangeY5), (rangeX6,rangeY6), (255,0,255), thickness=1, lineType=8, shift=0)
            #cv2.rectangle(frame, (rangeX7,rangeY7), (rangeX8,rangeY8), (255,0,255), thickness=1, lineType=8, shift=0)
            
            #if self.raspberry == False:
            #    cv2.imshow('frame', frame)
            if cv2.waitKey(2) & 0xFF == ord('q'): # Warten für x millisekunden
                break
        
        # When everything done, release the capture
        cap.release()
        
        if self.raspberry == False:
            cv2.destroyAllWindows()
    
    def CheckPositionDepth(self, container):
        '''
        Prueft ob sich der Container innerhalb des Greifers befindet
        
        Kleiner 0:          Zu weit weg
        Groesser gleich 0:  Positioniert
        '''
        
        if (container is None):
            return -10

        return container.GetFlaeche() - 100000
    
    
    def GetthresholdedimgBlue(self, hsv):
        #blue = cv2.inRange(hsv,np.array((100,0,100)),np.array((120,255,255)))
        blue = cv2.inRange(hsv,np.array((106,6,34)),np.array((164,255,255)))
        return blue
    
    
    def GetthresholdedimgYellow(self, hsv):
        #yellow = cv2.inRange(hsv,np.array((0,115,84)),np.array((217,255,171)))
        yellow = cv2.inRange(hsv,np.array((20,6,34)),np.array((40,255,255)))
        return yellow
    
    
    def GetthresholdedimgBoth(self, hsv):
        return self.GetthresholdedimgBlue(hsv)
        #both = cv2.add(self.GetthresholdedimgBlue(hsv),self.GetthresholdedimgYellow(hsv))
        #return both
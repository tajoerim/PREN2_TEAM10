'''
Created on 04.03.2016

@author: Christoph
@todo: Methoden implementieren
'''

#import hslu.pren.common
#from random import randint


#class Navigator():
    
#    #Constructor
#    def __init__(self, webcamPort):
#        self.port = webcamPort
        
#    def GetCorrectionAngle(self):
        
#        return randint(-25, 25)
        
#        # SIEHE DIESE WEBSITE: http://roboticssamy.blogspot.ch/

import hslu.pren.common
import threading
import cv2
import numpy as np

class Navigator(threading.Thread):

    FRAME_HEIGHT = 240
    FRAME_WIDTH = 320
    FPS = 24
    SPLIT_NUM = 24
    CENTER = 160
    RANGE = 40

    DEBUG = True

    # Constructor
    def __init__(self, webcamPort):
        threading.Thread.__init__(self)
        self.port = webcamPort
        self.distance = 0

    def getDistance(self):
        return self.distance

    def setDistance(self, mat):
        self.distance = (mat[self.SPLIT_NUM/2][0])-self.CENTER

    # split frame
    def split(self,mat):
        matset = []
        x1 = self.CENTER - self.RANGE
        x2 = self.CENTER + self.RANGE
        for i in range(self.SPLIT_NUM):
            y1 = (self.FRAME_HEIGHT/self.SPLIT_NUM)*i
            y2 = (self.FRAME_HEIGHT/self.SPLIT_NUM)*(i+1)
            m = mat[y1:y2, x1:x2]
            matset.append(m)
        return matset

    # get list of center points
    def getCenters(self, matset):
        centers = []
        for i in range(len(matset)-1,-1,-1):
            m = cv2.moments(matset[i])
            if m['m00'] != 0:
                x = int(m['m10']/m['m00'])
                y = int(m['m01']/m['m00'])
                y += self.FRAME_HEIGHT/self.SPLIT_NUM*i
                x += self.CENTER - self.RANGE
                centers.append((x, y))
            else:
                if len(centers) > 0:
                    x, y = centers[len(centers)-1]
                    p = (x, y - self.FRAME_HEIGHT/self.SPLIT_NUM)
                    centers.append(p)
                else:
                    x = self.CENTER
                    y = int((self.FRAME_HEIGHT/self.SPLIT_NUM) * (i+0.5))
                    centers.append((x, y))
        return centers

    # set frame size and fps
    def setCam(self):
        if (self.DEBUG):
            cap = cv2.VideoCapture(0)
        else:
            cap = cv2.VideoCapture(self.port)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        cap.set(cv2.cv.CV_CAP_PROP_FPS, self.FPS)
        return cap

    # start cam
    def run(self):
        cap = self.setCam()
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Otsu's thresholding after Gaussian filtering
            blur = cv2.GaussianBlur(gray,(5,5),0)
            ret1, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            # calculate centers
            m = self.getCenters(self.split(th))
            self.setDistance(m)

            # Display stuff to Debug
            if self.DEBUG:
                text = str(self.getDistance())
                cv2.putText(frame,text,(10,220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

                for i in range(1,len(m)):
                    cv2.line(frame,m[i-1],m[i],(0,0,255),3)

                cv2.imshow('original',frame)
                cv2.imshow('OTSU',th)
                cv2.moveWindow('OTSU',340,0)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        if self.DEBUG:
            cv2.destroyAllWindows()

﻿'''
Created on 04.03.2016

@author: Christoph
@todo: Methoden implementieren
'''

#import hslu.pren.common
#from random import randint

import hslu.pren.common
from hslu.pren.communication import *

import threading
import cv2
import numpy as np
import sys
import time

class Navigator(threading.Thread):

    FRAME_HEIGHT = 240
    FRAME_WIDTH = 320
    FPS = 24
    SPLIT_NUM = 24
    CENTER = 160
    RANGE = 120

    SOLL_WINKEL_ADD = 0 # Fuer spaeter, wenn wir die Webcam schraeg stellen muss dieser hier dementsprechend angepasst werden
    TOLLERANCE_TO_CENTER = 50 # Die Tolleranz welche Punkte zum durchschnitt haben koennen. Ausreisser werden so eliminiert
    WINKEL_MULTIPLIKATOR = 2 # Eine groessere Zahl bewirkt eine extremere Korrektur

    # Constructor
    def __init__(self, webcamPort, debug=False):
        threading.Thread.__init__(self)
        self.port = webcamPort
        self.distance = 0
        self.debug = debug

    def getDistance(self):
        return self.distance

    def setDistance(self, mat):
        #dist = (mat[self.SPLIT_NUM/2][0])-self.CENTER
        sum = 0
        for point in mat:
            sum = sum + point[0]

        self.distance = (((sum / len(mat)) - self.CENTER ) * self.WINKEL_MULTIPLIKATOR) + self.SOLL_WINKEL_ADD

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

            x = self.CENTER
            y = int((self.FRAME_HEIGHT/self.SPLIT_NUM) * (i+0.5))
            defaultP = (x,y)

            m = cv2.moments(matset[i])
            if m['m00'] != 0:
                x = int(m['m10']/m['m00'])
                y = int(m['m01']/m['m00'])
                y += self.FRAME_HEIGHT/self.SPLIT_NUM*i
                x += self.CENTER - self.RANGE

                if (x < self.CENTER + self.TOLLERANCE_TO_CENTER and x > self.CENTER - self.TOLLERANCE_TO_CENTER):
                    p = (x, y - self.FRAME_HEIGHT/self.SPLIT_NUM)
                    centers.append(p)
                else:
                    centers.append(defaultP)

            else:
                if len(centers) > 0:
                    x, y = centers[len(centers)-1]

                    if (x < self.CENTER + self.TOLLERANCE_TO_CENTER and x > self.CENTER - self.TOLLERANCE_TO_CENTER):
                        p = (x, y - self.FRAME_HEIGHT/self.SPLIT_NUM)
                    else:
                        centers.append(defaultP)
                else:
                    centers.append(defaultP)

        return centers

    # set frame size and fps
    def setCam(self):
        if (self.debug):
            #cap = cv2.VideoCapture(0)
            cap = cv2.VideoCapture('D:\Dropbox\Dropbox\PREN_TEAM_10\PREN2\Navigator\spur.mp4')
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
            try:
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Otsu's thresholding after Gaussian filtering
                blur = cv2.GaussianBlur(gray,(3, 3),0)
                ret1, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                # calculate centers
                centers = self.getCenters(self.split(th))
                #self.CENTER = ((centers[0][1] + centers[1][1] + centers[2][1]) / 3)
                distance = self.setDistance(centers)

                # Display stuff to Debug
                if self.debug:
                    text = str(self.getDistance())
                    cv2.putText(frame,text,(10,220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

                    for i in range(1,len(centers)):
                        cv2.line(frame,centers[i-1],centers[i],(0,0,255),3)

                    xDriveLine = centers[0][0]
                    cv2.line(frame,(self.distance + self.CENTER, 0),(self.CENTER, self.FRAME_HEIGHT),(255,0,0),3)
                    cv2.line(frame,((self.CENTER - self.TOLLERANCE_TO_CENTER / 2) + self.SOLL_WINKEL_ADD, 0),(self.CENTER - self.TOLLERANCE_TO_CENTER / 2, self.FRAME_HEIGHT),(0,255,0),1)
                    cv2.line(frame,((self.CENTER + self.TOLLERANCE_TO_CENTER / 2) + self.SOLL_WINKEL_ADD, 0),(self.CENTER + self.TOLLERANCE_TO_CENTER / 2, self.FRAME_HEIGHT),(0,255,0),1)

                    cv2.imshow('OTSU',th)
                    cv2.imshow('original',frame)
            except:
                 print "Hoppla"

            if cv2.waitKey(50) & 0xFF == ord('q'):
                break

        cap.release()
        if self.debug:
            cv2.destroyAllWindows()



class NavigatorAgent(threading.Thread):

    INTERVAL_SECONDS = 0.25

    # Constructor
    def __init__(self, freedom, webcamPort, debug):
        threading.Thread.__init__(self)
        self.freedom = freedom
        self.webcamPort = webcamPort
        self.debug = debug
        self.running = True
        self.waiting = False

    def run(self):

        print "Initialize navigator"
        navigator = Navigator(self.webcamPort, self.debug)
        navigator.start()
        print "navigator initialized"

        while (self.running):
            if (self.waiting): # Wenn das Fhz steht, dann warten wir bis wir wieder fahren. Sonst korrigieren wir ins unendliche!
                time.sleep(1)
            else:
                time.sleep(self.INTERVAL_SECONDS)

                correction = navigator.getDistance()
                self.freedom.setDriveAngle(correction)
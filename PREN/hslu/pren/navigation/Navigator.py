'''
Created on 04.03.2016

@author: Christoph
@todo: Methoden implementieren
'''

#import hslu.pren.common
#from random import randint

import hslu.pren.common
from hslu.pren.communication import *
from hslu.pren.navigation import CameraProfile

import threading
import cv2
import numpy as np
import sys
import time

class Navigator(threading.Thread):

    FRAME_HEIGHT = 240
    FRAME_WIDTH = 320
    FPS = 24
    SPLIT_NUM = 12
    CENTER = 170
    RANGE = 100
    
    DRIVE_METHOD_MAX = 1
    DRIVE_METHOD_AVG = 2
    MOMENT_ADD_X = 10

    SOLL_WINKEL_ADD = 0 # Fuer spaeter, wenn wir die Webcam schraeg stellen muss dieser hier dementsprechend angepasst werden
    TOLLERANCE_TO_CENTER = 270 # Die Tolleranz welche Punkte zum durchschnitt haben koennen. Ausreisser werden so eliminiert
    WINKEL_MULTIPLIKATOR = 1 # Eine groessere Zahl bewirkt eine extremere Korrektur

    # Constructor
    def __init__(self, webcamPort, freedom, debug=False):
        threading.Thread.__init__(self)
        self.port = webcamPort
        self.distance = 0
        self.debug = debug
        self.driveMethod = 1
        self.running = True
        self.freedom = freedom
        self.manualCurve = False
        self.manualSpeed = False
        self.correction = 0

    def getDistance(self):
        return self.distance - self.SOLL_WINKEL_ADD

    def setDistance(self, mat):
        #dist = (mat[self.SPLIT_NUM/2][0])-self.CENTER

        max = 0
        for point in mat:
            if (point[0] > max):
                max = point[0]
        max = ((max - self.CENTER) * self.WINKEL_MULTIPLIKATOR) + self.SOLL_WINKEL_ADD

        sum = 0
        for point in mat:
            sum =  sum + point[0]

        avg = (((sum / len(mat)) - self.CENTER ) * self.SOLL_WINKEL_ADD)

        self.distance = ((avg + max) / 2)  + self.WINKEL_MULTIPLIKATOR # Wir fahren einen Mittelwert zwische dem Durchschnitt der linie und dem Punkt ganz rechts. (Wir wollen eher rechts fahren und der rechten Linie folgen)
        return self.distance

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

                p = (x, y - self.FRAME_HEIGHT/self.SPLIT_NUM)
                centers.append(p)

            else:
                if len(centers) > 0:
                    x, y = centers[len(centers)-1]
                    p = (x, y - self.FRAME_HEIGHT/self.SPLIT_NUM)
                else:
                    centers.append(defaultP)

        return centers

    # set frame size and fps
    def setCam(self):
        if (self.debug):
            #cap = cv2.VideoCapture(0)
            cap = cv2.VideoCapture('hslu/pren/navigation/spur.mp4')
            #cap = cv2.VideoCapture('hslu/pren/navigation/output8.avi')
        else:
            if (self.isInt(self.port)):
                cap = cv2.VideoCapture(int(self.port))
            else:
                cap = cv2.VideoCapture(self.port)

        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        cap.set(cv2.cv.CV_CAP_PROP_FPS, self.FPS)

        return cap


    def nothing(*arg):
        pass

    # start cam
    def run(self):
        cap = self.setCam()

        
        if (self.debug):
            cv2.namedWindow('original')
            cv2.createTrackbar('CENTER', 'original', self.CENTER, self.FRAME_WIDTH, self.nothing)
            cv2.createTrackbar('RANGE', 'original', self.RANGE, 200, self.nothing)
            cv2.createTrackbar('BRIGHT', 'original', int(cap.get(cv2.cv.CV_CAP_PROP_BRIGHTNESS)), 255, self.nothing)

        while (self.running):
            try:

                if (self.debug):
                    self.CENTER = cv2.getTrackbarPos('CENTER', 'original')
                    self.RANGE = cv2.getTrackbarPos('RANGE', 'original')
                    cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, cv2.getTrackbarPos('BRIGHT', 'original')) 
        
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Otsu's thresholding after Gaussian filtering
                blur = cv2.GaussianBlur(gray,(3, 3),0)


                ret1, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                # calculate centers
                centers = self.getCenters(self.split(th))
                distance = self.setDistance(centers)

                # Display stuff to Debug
                if self.debug:

                    for i in range(1,len(centers)):
                        cv2.line(frame,centers[i-1],centers[i],(0,0,255),1)

                    cv2.line(frame,(self.distance + self.CENTER, 0),(self.distance + self.CENTER, self.FRAME_HEIGHT),(0,0,255),3)
                    cv2.line(frame,((self.CENTER) + self.SOLL_WINKEL_ADD, 0),(self.CENTER, self.FRAME_HEIGHT),(0,255,0),2)

                    #cv2.imshow('OTSU',th)
                    cv2.imshow('original',frame)
                    
            except KeyboardInterrupt:
                self.running = False

            except:
                self.distance = 0
                print "Hoppla"

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        if self.debug:
            cv2.destroyAllWindows()


    def isInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False
    
from hslu.pren.navigation import PID

class NavigatorAgent(threading.Thread):

    INTERVAL_SECONDS = 0.05

    # Constructor
    def __init__(self, freedom, webcamPort, debug):
        threading.Thread.__init__(self)
        self.freedom = freedom
        self.webcamPort = webcamPort
        self.debug = debug
        self.running = True
        self.waiting = False

    def getManualSpeed(self):
        return self.navigator.manualSpeed

    def run(self):

        print "Initialize navigator"
        self.navigator = Navigator(self.webcamPort, self.freedom, self.debug)
        self.navigator.start()
        print "navigator initialized"

        pid = PID.PID(1.2, 1, 0.001)
        pid.SetPoint=0.0
        pid.setSampleTime(0.01)

        while (self.running):
            try:
                if (self.waiting): # Wenn das Fhz steht, dann warten wir bis wir wieder fahren. Sonst korrigieren wir ins unendliche!
                    time.sleep(1)
                else:
                    time.sleep(self.INTERVAL_SECONDS)

                    correction = self.navigator.getDistance()
                    pid.update(correction)
                    pidValue = pid.output * -1
                    self.freedom.setDriveAngle(pidValue)

                    if (self.debug):
                        strValue = "  "
                        if (pidValue < -100):
                            strValue += "-----|----#   "
                        elif (pidValue < -80):
                            strValue += "-----|---#-   "
                        elif (pidValue < -60):
                            strValue += "-----|--#--   "
                        elif (pidValue < -40):
                            strValue += "-----|-#---   "
                        elif (pidValue < -20):
                            strValue += "-----|#----   "

                        
                        elif (pidValue > 100):
                            strValue += "#----|-----   "
                        elif (pidValue > 80):
                            strValue += "-#---|-----   "
                        elif (pidValue > 60):
                            strValue += "--#--|-----   "
                        elif (pidValue > 40):
                            strValue += "---#-|-----   "
                        elif (pidValue > 20):
                            strValue += "----#|-----   "

                        else:
                            strValue += "-----|-----   "

                        if (pidValue < 0):
                            strValue += "  fahrt: <--  "
                        else:
                            strValue += "  fahrt: -->  "

                        strValue += "Correction: " + str(correction) + " => PID: " + str(pidValue)

                        print strValue
                    
            except KeyboardInterrupt:
                self.freedom.stop()
                self.navigator.running = False
                return

        self.navigator.running = False # stopping navigator
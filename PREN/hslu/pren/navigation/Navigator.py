'''
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

    FRAME_HEIGHT = 480
    FRAME_WIDTH = 640
    FPS = 24
    SPLIT_NUM = 24
    CENTER = 420
    RANGE = 120

    DRIVE_METHOD_MAX = 1
    DRIVE_METHOD_AVG = 2

    SOLL_WINKEL_ADD = 200 # Fuer spaeter, wenn wir die Webcam schraeg stellen muss dieser hier dementsprechend angepasst werden
    TOLLERANCE_TO_CENTER = 250 # Die Tolleranz welche Punkte zum durchschnitt haben koennen. Ausreisser werden so eliminiert
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

        avg = (((sum / len(mat)) - self.CENTER ) * self.WINKEL_MULTIPLIKATOR) + self.SOLL_WINKEL_ADD

        self.distance = (avg + max) / 2 # Wir fahren einen Mittelwert zwische dem Durchschnitt der linie und dem Punkt ganz rechts. (Wir wollen eher rechts fahren und der rechten Linie folgen)
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
            #cap = cv2.VideoCapture(1)
            #cap = cv2.VideoCapture('hslu/pren/navigation/spur.mp4')
            cap = cv2.VideoCapture('hslu/pren/navigation/output2.avi')
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
            cv2.createTrackbar('SOLL_WINKEL_ADD', 'original', self.SOLL_WINKEL_ADD, 500, self.nothing)
            cv2.createTrackbar('TOLLERANCE_TO_CENTER', 'original', self.TOLLERANCE_TO_CENTER, 500, self.nothing)
            cv2.createTrackbar('WINKEL_MULTIPLIKATOR', 'original', self.WINKEL_MULTIPLIKATOR, 3, self.nothing)

            
            cv2.namedWindow('OTSU')
            cv2.createTrackbar('BRIGHT', 'OTSU', int(cap.get(cv2.cv.CV_CAP_PROP_BRIGHTNESS)), 255, self.nothing)
            cv2.createTrackbar('CONTR', 'OTSU', int(cap.get(cv2.cv.CV_CAP_PROP_CONTRAST)), 255, self.nothing)
            cv2.createTrackbar('SATUR', 'OTSU', int(cap.get(cv2.cv.CV_CAP_PROP_SATURATION)), 100, self.nothing)
            cv2.createTrackbar('HUE', 'OTSU', int(cap.get(cv2.cv.CV_CAP_PROP_HUE)), 100, self.nothing)

            cv2.createTrackbar('THRESH1', 'OTSU', 0, 255, self.nothing)
            cv2.createTrackbar('THRESH2', 'OTSU', 255, 255, self.nothing)

            cv2.createTrackbar('SLOW', 'OTSU', 100, 1000, self.nothing)

            
            #cv2.namedWindow('Controller')
            cv2.createTrackbar('DRIVE', 'original', 0, 1, self.nothing)
            cv2.createTrackbar('SPEED', 'original', 500, 10000, self.nothing)
            cv2.createTrackbar('CURVE', 'original', 0, 2, self.nothing)

            
        while (self.running):
            try:

                if (self.debug):
                    self.CENTER = cv2.getTrackbarPos('CENTER', 'original')
                    self.RANGE = cv2.getTrackbarPos('RANGE', 'original')
                    self.SOLL_WINKEL_ADD = cv2.getTrackbarPos('SOLL_WINKEL_ADD', 'original')
                    self.TOLLERANCE_TO_CENTER = cv2.getTrackbarPos('TOLLERANCE_TO_CENTER', 'original')
                    self.WINKEL_MULTIPLIKATOR = cv2.getTrackbarPos('WINKEL_MULTIPLIKATOR', 'original')
                    
                    cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, cv2.getTrackbarPos('BRIGHT', 'OTSU')) 
                    cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, cv2.getTrackbarPos('CONTR', 'OTSU')) 
                    cap.set(cv2.cv.CV_CAP_PROP_SATURATION, cv2.getTrackbarPos('SATUR', 'OTSU')) 
                    cap.set(cv2.cv.CV_CAP_PROP_HUE, cv2.getTrackbarPos('HUE', 'OTSU')) 

                    if (cv2.getTrackbarPos('DRIVE', 'original') == 1):
                        self.manualSpeed = True
                        self.freedom.setSpeed(cv2.getTrackbarPos('SPEED', 'original'))
                    else:
                        self.manualSpeed = False

                    curve = cv2.getTrackbarPos('CURVE', 'original')
                    if (curve != 0):
                        self.manualCurve = True
                        if (curve == 1):
                            self.freedom.setDriveAngle(-50)
                        elif (curve == 2):
                            self.freedom.setDriveAngle(50)
                    else:
                        self.manualCurve = False
        
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Otsu's thresholding after Gaussian filtering
                blur = cv2.GaussianBlur(gray,(3, 3),0)

                th1 = 0
                th2 = 255
                if(self.debug):
                    th1 = cv2.getTrackbarPos('THRESH1', 'OTSU')
                    th2 = cv2.getTrackbarPos('THRESH2', 'OTSU')

                ret1, th = cv2.threshold(blur,th1,th2,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                # calculate centers
                centers = self.getCenters(self.split(th))
                distance = self.setDistance(centers)

                # Display stuff to Debug
                if self.debug:

                    cv2.putText(frame,"Cen: " + str(self.CENTER),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
                    cv2.putText(frame,"Tol: " + str(self.TOLLERANCE_TO_CENTER),(10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
                    cv2.putText(frame,str(self.getDistance()),(10,220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

                    for i in range(1,len(centers)):
                        cv2.line(frame,centers[i-1],centers[i],(0,0,255),1)

                    if (distance):
                        self.CENTER = self.CENTER + distance
                        if (self.CENTER < 150):
                            self.CENTER = 150
                        if (self.CENTER > 190):
                            self.CENTER = 190

                    xDriveLine = centers[0][0]
                    cv2.line(frame,(self.distance + self.CENTER, 0),(self.CENTER, self.FRAME_HEIGHT),(255,0,0),3)
                    cv2.line(frame,((self.CENTER) + self.SOLL_WINKEL_ADD, 0),(self.CENTER, self.FRAME_HEIGHT),(255,0,0),2)
                    cv2.line(frame,((self.CENTER - self.TOLLERANCE_TO_CENTER) + self.SOLL_WINKEL_ADD, 0),(self.CENTER - self.TOLLERANCE_TO_CENTER, self.FRAME_HEIGHT),(0,255,0),1)
                    cv2.line(frame,((self.CENTER + self.TOLLERANCE_TO_CENTER) + self.SOLL_WINKEL_ADD, 0),(self.CENTER + self.TOLLERANCE_TO_CENTER, self.FRAME_HEIGHT),(0,255,0),1)

                    if (self.manualSpeed):
                        cv2.rectangle(frame, (0,0), (self.FRAME_WIDTH, self.FRAME_HEIGHT), (0,255,0), 3)
                    else:
                        cv2.rectangle(frame, (0,0), (self.FRAME_WIDTH, self.FRAME_HEIGHT), (255,0,0), 3)

                    cv2.imshow('OTSU',th)
                    cv2.imshow('original',frame)
                    
            except KeyboardInterrupt:
                self.running = False

            except:
                 print "Hoppla"

            if (self.debug):
                time = cv2.getTrackbarPos('SLOW', 'OTSU')
                if (time > 10):
                    if cv2.waitKey(time) & 0xFF == ord('q'):
                        break
            else:
                if cv2.waitKey(10) & 0xFF == ord('q'):
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

    def getManualSpeed(self):
        return self.navigator.manualSpeed

    def run(self):

        print "Initialize navigator"
        self.navigator = Navigator(self.webcamPort, self.freedom, self.debug)
        self.navigator.start()
        print "navigator initialized"

        while (self.running):
            try:
                if (self.waiting): # Wenn das Fhz steht, dann warten wir bis wir wieder fahren. Sonst korrigieren wir ins unendliche!
                    time.sleep(1)
                else:
                    time.sleep(self.INTERVAL_SECONDS)
                    correction = self.navigator.getDistance()
                    
                    if (self.navigator.manualCurve == False):
                        self.freedom.setDriveAngle(correction)
                    
            except KeyboardInterrupt:
                self.navigator.running = False
                return

        self.navigator.running = False # stopping navigator
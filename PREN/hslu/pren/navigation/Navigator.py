'''
Created on 04.03.2016

@author: Christoph
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
import imutils

from picamera.array import PiRGBArray
from picamera import PiCamera

class Navigator(threading.Thread):
    FRAME_HEIGHT = 240
    FRAME_WIDTH = 240
    FPS = 24
    SPLIT_NUM = 12
    CENTER = 160
    ANGLE = 50

    # Constructor
    def __init__(self, raspberry, debug):
        threading.Thread.__init__(self)
        self.raspberry = raspberry
        self.distance = 0
        self.DEBUG = debug
        self.running = True
        self.startZiel = False
        self.searchLine = False
        self.line = []
        self.iniitLine()

    # set frame size and fps
    def setCam(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        cap.set(cv2.cv.CV_CAP_PROP_FPS, self.FPS)
        return cap
    
    def isInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False

    def getDistance(self):
        return self.distance

    def setDistance(self, mat):
        self.distance = (mat[self.SPLIT_NUM / 2][0]) - self.CENTER

    # split frame
    def split(self, frame):
        copy = frame.copy()
        partset = []
        x1 = 0
        x2 = self.FRAME_WIDTH
        for i in range(self.SPLIT_NUM):
            y1 = (self.FRAME_HEIGHT / self.SPLIT_NUM) * i
            y2 = (self.FRAME_HEIGHT / self.SPLIT_NUM) * (i + 1)
            part = copy[y1:y2, x1:x2]
            partset.append(part)
        return partset

    # init line array with points
    def iniitLine(self):
        for i in range(10, self.FRAME_WIDTH, 10):
            self.line.append((120, i))

    # finde start/ziel linie
    def findStartFinishLine(self, frame):
        found = False
        aLine = []
        for p in self.line:
            if frame[p] == 255:
                aLine.append((p[1], p[0]))
        if len(aLine) >= 30:
            found = True
        return found

    # set bool
    def setStartZiel(self, found):
        self.startZiel = found

    # get bool
    def geStartZiel(self):
        return self.startZiel

    # set bool
    def setSearchLine(self, search):
        self.searchLine = search

    # get bool
    def getSearchLine(self):
        return self.searchLine

    # find contours of splited frame and calc there rightmost points
    def findPoints(self, splitset):
        partcnt = []
        for i in range(self.SPLIT_NUM):
            contours, h = cv2.findContours(splitset[i], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            points = []
            for cnt in contours:
                rm = tuple(cnt[cnt[:, :, 0].argmax()][0])
                rightmost = (int(rm[0]), int(rm[1]) + self.FRAME_HEIGHT / self.SPLIT_NUM * i)
                points.append(rightmost)
            partcnt.append(points)
        return partcnt

    # find contours
    def findContours(self, frame):
        copy = frame.copy()
        cnt = []
        contours, h = cv2.findContours(copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if 1000 < area < 10000 or area > 23000:
                (x, y), (MA, ma), angle = cv2.fitEllipse(c)
                if 0 < angle < self.ANGLE or 180 > angle > 180 - self.ANGLE:
                    cnt.append(c)
        return cnt

    # check if points in contour
    def checkPoints(self, contours, points):
        i = 0
        checkedPoints = []
        for pset in points:
            pointset = []
            for point in pset:
                for cnt in contours:
                    test = cv2.pointPolygonTest(cnt, point, False)
                    if test != -1:
                        pointset.append(point)
            if len(pointset) > 0:
                checkedPoints.append(max(pointset))
            else:
                if len(checkedPoints) > 0:
                    lastpoint = checkedPoints[i-1]
                    newpoint = (lastpoint[0], lastpoint[1]+self.FRAME_HEIGHT/self.SPLIT_NUM)
                    checkedPoints.append(newpoint)
                else:
                    default = (self.CENTER, int(self.FRAME_HEIGHT/self.SPLIT_NUM*(i+0.5)))
                    checkedPoints.append(default)
            i += 1
        return checkedPoints

    #draw contour
    def drawContours(self, contours, target):
        if len(contours) > 0:
            cv2.drawContours(target, contours, -1, (0, 255, 0), 2)

    # start cam
    def run(self):

        if (self.raspberry):
            camera = PiCamera()
            camera.resolution = (self.FRAME_WIDTH, self.FRAME_HEIGHT)
            camera.framerate = 24
            camera.ISO = 800
            camera.rotation = 90

            time.sleep(1)

            stream = PiRGBArray(camera, size=(self.FRAME_WIDTH, self.FRAME_HEIGHT))

            for f in camera.capture_continuous(stream, format="bgr", use_video_port=True):

                if (self.running == False):
                    return

                self.calc(stream.array)

                stream.truncate(0)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        else:
            cap = self.setCam()

            while (self.running):
                ret, frame = cap.read()
                frame = imutils.rotate(frame, 90)
                self.calc(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

    def calc(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        ret1, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # calculate points
        contours = self.findContours(th)
        split = self.split(th)
        points = self.findPoints(split)
        chp = self.checkPoints(contours, points)
        self.setDistance(chp)

        # Display stuff to Debug
        #if self.DEBUG:
        text = str(self.getDistance())
        cv2.putText(frame, text, (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        self.drawContours(contours, frame)
        # draw points
        for p in chp:
            cv2.circle(frame, p, 1, (255, 0, 0), 5)
        # draw line
        for i in range(1, len(chp)):
            cv2.line(frame, chp[i - 1], chp[i], (0, 0, 255), 2)

        cv2.imshow('original', frame)
        #cv2.imshow('OTSU', th)
        #cv2.moveWindow('OTSU', 340, 0)
    
from hslu.pren.navigation import PID

class NavigatorAgent(threading.Thread):

    INTERVAL_SECONDS = 0.25

    # Constructor
    def __init__(self, freedom, raspberry, debug):
        threading.Thread.__init__(self)
        self.freedom = freedom
        self.raspberry = raspberry
        self.debug = debug
        self.running = True
        self.waiting = False

    def run(self):

        # print"[NAVI] Initialize navigator"
        self.navigator = Navigator(self.raspberry, self.debug)
        self.navigator.start()
        # print"[NAVI] navigator initialized"

        pid = PID.PID(1.2, 1, 0.001)
        pid.SetPoint=0.0
        pid.setSampleTime(0.01)

        lastCorrection = 0;

        while (self.running == True):
            try:
                if (self.waiting): # Wenn das Fhz steht, dann warten wir bis wir wieder fahren. Sonst korrigieren wir ins unendliche!
                    time.sleep(1)
                else:
                    time.sleep(self.INTERVAL_SECONDS)

                    correction = self.navigator.getDistance()

                    # Weil wir in der Kurve die linie verlieren können, fahren wir einfach so weiter
                    if (lastCorrection > 10 and correction == 0):
                        correction = lastCorrection + 40
                    elif (lastCorrection < -10 and correction == 0):
                        correction = lastCorrection - 40
                    else:
                        lastCorrection = correction

                    pid.update(correction)
                    pidValue = pid.output
                    if (pidValue != 0):
                        pidValue = pidValue * -1

                        
                    # print"[NAVI] PID: " + str(pidValue)

                    self.freedom.setDriveAngle(pidValue)
                    
            except KeyboardInterrupt:
                self.freedom.stop()
                self.navigator.running = False
                self.running = False

        
        # print"[NAVI] Stopping navigator"
        self.navigator.running = False # stopping navigator
        sys.exit()
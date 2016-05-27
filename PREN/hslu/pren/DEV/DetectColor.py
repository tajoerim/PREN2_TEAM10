## Color Tracking v1.0
## Copyright (c) 2013-2014 Abid K and Jay Edry
## You may use, redistribute and/or modify this program it under the terms of the MIT license (https://github.com/abidrahmank/MyRoughWork/blob/master/license.txt).


''' v 0.1 - It tracks two objects of blue and yellow color each '''


import sys


sys.path.append('/usr/local/lib/python2.7/site-packages')

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import time
import sys
import imutils




scale = 1
width = 320 * scale
height = 240 * scale

rectx1 = 50
recty1 = 0
rectx2 = width - 50
recty2 = height
	
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 32
camera.ISO = 800
#camera.rotation = 270
time.sleep(2)


# define range of blue color in HSV
lower_blue = np.array([0, 50, 100])
upper_blue = np.array([255, 255, 255])
    
stream = PiRGBArray(camera, size=(width, height))

for f in camera.capture_continuous(stream, format="bgr", use_video_port=True):
    frame = stream.array
	
	# Convert BGR to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
	
    # Bitwise-AND mask and original image
    #res = cv2.bitwise_and(frame,frame, mask= mask)
    
    contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    maxw = 0
    maxh = 0
    
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        if w > maxw and h > maxh:
            maxw = w
            maxh = h
            x1 = x
            y1 = y
            x2 = x + maxw
            y2 = y + maxh
	
    if x1 > rectx1 and y1 > recty1 and x2 < rectx2 and y2 < recty2 and x1 < rectx2 and y1 < recty2 and x2 > rectx1 and y2 > recty1:
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0))
        print "Object found in range %s %s %s %s" % (x1, y1, x2, y2)
    else:
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255))
    
    cv2.rectangle(frame, (rectx1,recty1), (rectx2,recty2), (0,255,0))
    
    stream.truncate(0)
	
    cv2.imshow('frame',frame)
    #cv2.imshow('mask',mask)
    #cv2.imshow('res',res)
	
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print "BYE TEAM 10 :D"
        break

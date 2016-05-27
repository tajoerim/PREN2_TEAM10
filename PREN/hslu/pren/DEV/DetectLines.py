## Color Tracking v1.0
## Copyright (c) 2013-2014 Abid K and Jay Edry
## You may use, redistribute and/or modify this program it under the terms of the MIT license (https://github.com/abidrahmank/MyRoughWork/blob/master/license.txt).


''' v 0.1 - It tracks two objects of blue and yellow color each '''

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import time

width = 320
height = 240

rectx1 = 50
recty1 = 0
rectx2 = 250
recty2 = height

minLineLength = 1
maxLineGap = 10
	
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 60
camera.ISO = 800
time.sleep(2)

stream = PiRGBArray(camera, size=(width, height))

for f in camera.capture_continuous(stream, format="bgr", use_video_port=True):
    src = stream.array

    linecount = 0
	
	# Convert BGR to HSV
    hsv = cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
    edges = cv2.Canny(hsv,50,150,apertureSize = 3)

    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
    if lines is not None:
        for x1,y1,x2,y2 in lines[0]:
            if x1 > rectx1 and y1 > recty1 and x2 < rectx2 and y2 < recty2 and x1 < rectx2 and y1 < recty2 and x2 > rectx1 and y2 > recty1:
                #cv2.line(src,(x1,y1),(x2,y2),(0,0,255),2)
				linecount += 1

    #cv2.rectangle(src, (rectx1,recty1), (rectx2,recty2), (0,255,0))
			
    stream.truncate(0)

    #cv2.imshow('res',src)

    print linecount
	
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print "BYE TEAM 10 :D"
        break
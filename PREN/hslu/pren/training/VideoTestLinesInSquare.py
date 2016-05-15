'''
Created on 07.12.2015

@author: Christoph
'''

import numpy as np
import cv2

width = 320
height = 240

rectx1 = 50
recty1 = 0
rectx2 = 250
recty2 = height

minLineLength = 1
maxLineGap = 10
    
# initialize the camera and grab a reference to the raw camera capture
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    linecount = 0

    # Our operations on the frame come here
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    edges = cv2.Canny(hsv,50,150,apertureSize = 3)

    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
    if lines is not None:
        for x1,y1,x2,y2 in lines[0]:
            if x1 > rectx1 and y1 > recty1 and x2 < rectx2 and y2 < recty2 and x1 < rectx2 and y1 < recty2 and x2 > rectx1 and y2 > recty1:
                linecount += 1
                cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)

    cv2.rectangle(frame, (rectx1,recty1), (rectx2,recty2), (0,255,0))
    print linecount
    
    # Display the resulting frame
    cv2.imshow('frame',frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
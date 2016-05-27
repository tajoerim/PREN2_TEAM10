'''
Created on 07.12.2015

@author: Christoph
'''


import sys


sys.path.append('/usr/local/lib/python2.7/site-packages')

import numpy as np
import cv2
import time

width = 320
height = 240
    
# initialize the camera and grab a reference to the raw camera capture
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
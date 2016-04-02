'''
Created on 07.12.2015

@author: Christoph
'''

from Tkinter import *
import numpy as np
import cv2
from hslu.pren.common import Utilities
from hslu.pren.common import HsvColor



def doIt():
    # initialize the camera and grab a reference to the raw camera capture
    cap = cv2.VideoCapture(0)
    
    
    # define range of blue color in HSV
    colorRange = HsvColor.GetHsvColorFromRgb(w1.get(), w2.get(), w3.get())
        
    while(True):
    
        # Take each frame
        _, frame = cap.read()
    
        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, colorRange.lowerRange(w4.get(), w5.get(), w6.get()), colorRange.upperRange(w4.get(), w7.get(), w8.get()))
    
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame,frame, mask= mask)
    
        cv2.imshow('res',res)
        cv2.imshow('frame',frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()



master = Tk()
w1 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w1.pack()
w2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w2.pack()
w3 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w3.pack()

w4 = Scale(master, from_=0, to=50, orient=HORIZONTAL)
w4.set(10)
w4.pack()

w5 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w5.set(100)
w5.pack()
w6 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w6.set(100)
w6.pack()

w7 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w7.set(255)
w7.pack()
w8 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
w8.set(255)
w8.pack()

Button(master, text='Show', command=doIt).pack()
mainloop()


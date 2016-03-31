'''
Created on 08.12.2015

@author: Christoph
'''

import numpy as np
import cv2


class HsvColor():
    '''
    Hilfsklasse fuer Farbkonvertierung und Farbmaskierung in einem
    bestimmen Range
    '''
    
    def __init__(self, h="", s="", v=""):
        self.hue = h
        self.satturaion = s
        self.value = v
        
    def lowerRange(self, tollerance, hue, value):
        return np.array([self.hue - tollerance, hue, value])
    
    def upperRange(self, tollerance, hue, value):
        return np.array([self.hue + tollerance, 255, 255])
    
def GetHsvColorFromRgb(r, g, b):
    '''
    Konvertiert von RGB nach OpenCV HSV
    '''
    
    rgb = np.uint8([[[b,g,r]]])
    hsv_rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    print "(" + str(r) + ", " + str(g) + ", " + str(b) + ") = " + str(hsv_rgb)
    return HsvColor(hsv_rgb[0][0][0], hsv_rgb[0][0][1], hsv_rgb[0][0][2])
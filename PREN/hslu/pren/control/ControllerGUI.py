import threading
import cv2
import numpy as np
import sys
import time

class ControllerGUI(threading.Thread):


    # Constructor
    def __init__(self, freedom):
        threading.Thread.__init__(self)
        self.freedom = freedom
        self.running = True


    def run(self):

        cv2.namedWindow('Controller')
        cv2.createTrackbar('SPEED', 'Controller', 500, 10000, self.nothing)
        cv2.createTrackbar('CURVE', 'Controller', 0, 2, self.nothing)

        while (self.running):
            try:
                self.freedom.setSpeed(cv2.getTrackbarPos('SPEED', 'Controller'))

                curve = cv2.getTrackbarPos('CURVE', 'Controller')
                if (curve != 0):
                    if (curve == 1):
                        self.freedom.setDriveAngle(-50)
                    elif (curve == 2):
                        self.freedom.setDriveAngle(50)

                cv2.imshow('Controller',None)
                
                    
            except KeyboardInterrupt:
                self.running = False

            except:
                 print "Hoppla"

            if cv2.waitKey(100) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        

    def nothing(*arg):
        pass
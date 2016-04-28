from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import time
import sys

scale = 1
width = 320 * scale
height = 240 * scale

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 32
camera.ISO = 800
time.sleep(2)

stream = PiRGBArray(camera, size=(width, height))




# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter('/home/pi/Desktop/output7.avi',fourcc, 30.0, (640,480))

for f in camera.capture_continuous(stream, format="bgr", use_video_port=True):
    try:
        frame = stream.array

        # write the flipped frame
        out.write(frame)

    
        stream.truncate(0)
    
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    except KeyboardInterrupt:
        break

# Release everything if job is finished

out.release()
cv2.destroyAllWindows()
from hslu.pren.visuals import ContainerDetection
from hslu.pren.communication import FreedomBoard
import time

useFreedom = False
setSpeed = False

freedom = FreedomBoard.FreedomBoardCommunicator("/dev/ttyACM0", 9600, useFreedom)
containerDetecor = ContainerDetection.ContainerDetector('blue', 0, True)
containerDetecor.start()


if (useFreedom):
    while (True):
        freedom.closeGrabber()

        if (setSpeed):
            freedom.setSpeed(6000)

        container = containerDetecor.GetContainer()
        if (container is not None):
                    
            freedom.openGrabber()

            if (setSpeed):
                freedom.setSpeed(0)
                        
            # Greifer positionieren
            tryAgain = True
            while tryAgain:
                
                time.sleep(1)
                # Container neu erkennen um Position zu ermitteln
                container = containerDetecor.GetContainer() 
                
                if (container is not None):
                    position = container.relativeCenter
                            
                    if (position == 0 or position > 0):
                        freedom.setSpeed(0)
                        tryAgain = False
                                
                    elif (position < 0):
                        freedom.setSpeed(6000)
                
            #runter
            freedom.setGrabberPosition(0,2)
            freedom.setGrabberPosition(0,2)
                
            #nach vorne 
            cnt = 0
            while (containerDetecor.CheckPositionDepth(container) == False):
                cnt += 1
                freedom.setGrabberPosition(1,0)
                time.sleep(1)
                        
            freedom.closeGrabber()
        
            #hoch
            freedom.setGrabberPosition(0,1)
            freedom.setGrabberPosition(0,1)
            freedom.setGrabberPosition(0,1)
            freedom.setGrabberPosition(0,1)

            #nach hinten
            for x in range(cnt):
                freedom.setGrabberPosition(2,0)

            freedom.emptyContainer();

            #nach vorne
            for x in range(cnt):
                freedom.setGrabberPosition(1,0)

            #runter
            freedom.setGrabberPosition(0,2)
            freedom.setGrabberPosition(0,2)

            freedom.openContainer()

            #hoch
            freedom.setGrabberPosition(0,1)
            freedom.setGrabberPosition(0,1)
            freedom.setGrabberPosition(0,1)

            #nach hinten
            for x in range(cnt):
                freedom.setGrabberPosition(1,0)
        
            freedom.closeGrabber()
            
            freedom.setSpeed(6000)
            time.sleep(5)
else:
    while (True):

        print "normal Speed"

        # Objekt erkannt?
        container = containerDetecor.GetContainer()
        if (container is not None):
        
            print "Open grabber"            

            print "stop speed"
                        
            # Greifer positionieren
            tryAgain = True
            while tryAgain:
                
                time.sleep(1)
                # Container neu erkennen um Position zu ermitteln
                container = containerDetecor.GetContainer() 

                if (container is not None):

                    position = container.relativeCenter
                            
                    if (position == 0 or position > 0):
                        print "stop speed"
                        tryAgain = False
                                
                    elif (position < 0):
                        print "slow speed"
                
            #runter
            print "down"
            print "down"
                
            #nach vorne 
            cnt = 0
            while (containerDetecor.CheckPositionDepth(container) == False):
                cnt += 1
                print "nach vorne"
                time.sleep(1)

                # Container neu erkennen um Position zu ermitteln
                container = containerDetecor.GetContainer() 
                        
            print "close"
        
            #hoch
            print "hoch"
            print "hoch"
            print "hoch"
            print "hoch"

            #nach hinten
            for x in range(cnt):
                print "nach hinten"

            print "empty"

            #nach vorne
            for x in range(cnt):
                print "nach vorne"

            #runter
            print "runter"
            print "runter"

            print "open"

            #hoch
            print "hoch"
            print "hoch"
            print "hoch"

            #nach hinten
            for x in range(cnt):
                print "nach hinten"
        
            print "close"

            print "normal Speed"
            time.sleep(5)
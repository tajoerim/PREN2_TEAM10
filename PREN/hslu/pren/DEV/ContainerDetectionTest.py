from hslu.pren.visuals import ContainerDetection
from hslu.pren.communication import FreedomBoard
import time

useFreedom = True
setSpeed = True

port = raw_input("Set Port")

freedom = FreedomBoard.FreedomBoardCommunicator("/dev/ttyACM" + str(port), 9600, useFreedom)
containerDetecor = ContainerDetection.ContainerDetector('blue', 0, False, True)
containerDetecor.start()

try:
    if (useFreedom):
        time.sleep(5)

        freedom.initEngines(15000);

        while (True):

            container = containerDetecor.GetContainer();

            if (container is not None):
                freedom.stop();
                freedom.initEngines(15000);

                # Greifer positionieren
                tryAgain = True
                while tryAgain:
                    time.sleep(0.1)           
                    # Container neu erkennen um Position zu ermitteln
                    container = containerDetecor.GetContainer();
                    if (container is not None):
                        position = container.relativeCenter
                                
                        if (position < -20):
                            # print"zu weit vorne" + str(position)
                                
                        elif (position > 20):
                            # print"zu weit hinten" + str(position)
                            
                        else:
                            # print"positioniert!!!"
                            tryAgain = False
                            
                freedom.stop();    
                
                # print"flaeche" + str(container.GetFlaeche())

                while (container.GetFlaeche() < 30000):
                    # print"zu weit weg" + str(container.GetFlaeche())
                    freedom.setGrabberPosition(2,0)
                    container = containerDetecor.GetContainer();
                    time.sleep(0.1)
                    
                freedom.stop();
                # print"ok"
                time.sleep(0.2)
                freedom.closeGrabber();
                time.sleep(5)
                freedom.openGrabber();

                containerDetecor.running = False;

                freedom.stop();

                
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)

                break

            else:
                # print"NO CONTAINER"
                     
except KeyboardInterrupt:
    # print"BYE"
    containerDetecor.running = False;
    freedom.stop();
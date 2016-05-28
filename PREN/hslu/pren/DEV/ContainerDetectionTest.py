from hslu.pren.visuals import ContainerDetection
from hslu.pren.communication import FreedomBoard
import time
from hslu.pren.common import Logger

SPEED_STRAIGHT = 4000
SPEED_CURVE = 5000
SPEED_CROSSROAD = 7000
SPEED_DETECT = 5000
SPEED_POSITION_GRABBER = 7000
    
CONTAINER_FLAECHE = 25000
    
SEARCH_CONTAINER_COUNT = 2

logger = Logger.Logger("CTRL")

colorIdx = "2"


useFreedom = True
setSpeed = True

port = raw_input("Set Port")

freedom = FreedomBoard.FreedomBoardCommunicator("/dev/ttyACM" + str(port), 9600, useFreedom)
containerDetecor = ContainerDetection.ContainerDetector("2", 0, False, True)
containerDetecor.start()

print "Start"

try:
    while (True):
        if (containerDetecor.GetContainer() is not None):
            
            print "Container found"

            freedom.setLedBlue()

            freedom.stop();

            containerDetecor.wait = 1

            # Greifer positionieren
            tryAgain = True
            while tryAgain:
                time.sleep(0.1)           
                # Container neu erkennen um Position zu ermitteln
                container = containerDetecor.GetContainer();
                if (container is not None):
                    position = container.relativeCenter

                    color = logger.OKBLUE;
                    if (colorIdx == "1"):
                        color = logger.OKGREEN;

                    if (position < -20):
                        
                        logger.log("                                         ", color, False);
                        logger.log("                                         ", color, False);
                        logger.log("    _____________                        ", color, False);
                        logger.log("  ///////////////                        ", color, False);
                        logger.log(" ///////////////\                        ", color, False);
                        logger.log("##############/ /|                       ", color, False);
                        logger.log(" ############/ / |                       ", color, False);
                        logger.log("#############\/  |                       ", color, False);
                        logger.log("##############|  |                       ", color, False);
                        logger.log("##############|  |                       ", color, False);
                        logger.log("##############|  |                       ", color, False);
                        logger.log("##############|  /                       ", color, False);
                        logger.log("##############| /                        ", color, False);
                        logger.log("##############|/                         ", color, False);
                        logger.log(" ############/                           ", color, False);
                        logger.log("                                         ", logger.ENDC, False);
                        logger.log("       ___                     ___       ", logger.ENDC, False);
                        logger.log("       \##\                   /##/       ", logger.ENDC, False);
                        logger.log("          \##\             /##/          ", logger.ENDC, False);
                        logger.log("             \##\       /##/             ", logger.ENDC, False);
                        logger.log("                \##\ /##/                ", logger.ENDC, False);
                        logger.log("                                         ", logger.ENDC, False);
                        logger.log("                                         ", logger.ENDC, False);

                        logger.log("zu weit vorne: " + str(position), logger.HEADER)
                                
                    elif (position > 70):
                        
                        logger.log("                                         ", color, False);
                        logger.log("                                         ", color, False);
                        logger.log("                           _____________ ", color, False);
                        logger.log("                         /////////////// ", color, False);
                        logger.log("                        ///////////////\ ", color, False);
                        logger.log("                       ##############/ /|", color, False);
                        logger.log("                        ############/ / |", color, False);
                        logger.log("                       ##############/  |", color, False);
                        logger.log("                       ##############|  |", color, False);
                        logger.log("                       ##############|  |", color, False);
                        logger.log("                       ##############|  |", color, False);
                        logger.log("                       ##############|  /", color, False);
                        logger.log("                       ##############| / ", color, False);
                        logger.log("                       ##############|/  ", color, False);
                        logger.log("                        ############/    ", color, False);
                        logger.log("                                         ", color, False);
                        logger.log("                                         ", logger.ENDC, False);
                        logger.log("       ___                     ___       ", logger.ENDC, False);
                        logger.log("       \##\                   /##/       ", logger.ENDC, False);
                        logger.log("          \##\             /##/          ", logger.ENDC, False);
                        logger.log("             \##\       /##/             ", logger.ENDC, False);
                        logger.log("                \##\ /##/                ", logger.ENDC, False);
                        logger.log("                                         ", logger.ENDC, False);
                        logger.log("                                         ", logger.ENDC, False);

                        logger.log("zu weit hinten: " + str(position), logger.HEADER)
                            
                    else:
                        
                        logger.log("                                         ", color, False);
                        logger.log("                                         ", color, False);
                        logger.log("                 _____________           ", color, False);
                        logger.log("               ///////////////           ", color, False);
                        logger.log("              ///////////////\           ", color, False);
                        logger.log("             ##############/ /|          ", color, False);
                        logger.log("              ############/ / |          ", color, False);
                        logger.log("             ##############/  |          ", color, False);
                        logger.log("             ##############|  |          ", color, False);
                        logger.log("             ##############|  |          ", color, False);
                        logger.log("             ##############|  |          ", color, False);
                        logger.log("             ##############|  /          ", color, False);
                        logger.log("             ##############| /           ", color, False);
                        logger.log("             ##############|/            ", color, False);
                        logger.log("              ############/              ", color, False);
                        logger.log("                                         ", color, False);
                        logger.log("                                         ", logger.ENDC, False);
                        logger.log("       ___                     ___       ", logger.ENDC, False);
                        logger.log("       \##\                   /##/       ", logger.ENDC, False);
                        logger.log("          \##\             /##/          ", logger.ENDC, False);
                        logger.log("             \##\       /##/             ", logger.ENDC, False);
                        logger.log("                \##\ /##/                ", logger.ENDC, False);
                        logger.log("                                         ", logger.ENDC, False);
                        logger.log("                                         ", logger.ENDC, False);

                        logger.log("positioniert", logger.HEADER)
                        tryAgain = False
               
                        
            freedom.stop();
                                     
            freedom.openGrabber();
            freedom.stop();
                  
            freedom.setLedGreen()
                
            for x in range(0, 5):
                freedom.setGrabberPosition(2,0)
                time.sleep(0.1)

            for x in range(0, 12):
                freedom.setGrabberPosition(0,2)
                
            logger.log("Flaeche" + str(container.GetFlaeche()), logger.HEADER)

            while (container.GetFlaeche() < CONTAINER_FLAECHE):
                logger.log("zu weit weg" + str(container.GetFlaeche()), logger.HEADER)
                freedom.setGrabberPosition(2,0)
                container = None
                while (True):
                    container = containerDetecor.GetContainer();
                    if (container is not None):
                        break

                time.sleep(0.1)

            logger.log("ZUGRIFF", logger.WARNING);

            freedom.stop();
            freedom.closeGrabber();
            
            time.sleep(1)

            for x in range(0, 30):
                freedom.setGrabberPosition(0,1)

            for x in range(0, 10):
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)

            freedom.emptyContainer();
            time.sleep(3)

            for x in range(0, 12):
                freedom.setGrabberPosition(0,2)
                time.sleep(0.1)
                
            for x in range(0, 10):
                freedom.setGrabberPosition(2,0)
                time.sleep(0.1)

            freedom.openGrabber();
            freedom.stop();

            for x in range(0, 30):
                freedom.setGrabberPosition(0,1)

            for x in range(0, 10):
                freedom.setGrabberPosition(1,0)
                time.sleep(0.1)

            freedom.closeGrabber()

            logger.log("Container abschluss", logger.WARNING);
                        
            detectedContainers = detectedContainers + 1

            if (detectedContainers >= 2):
                logger.log("Container Erkennung deaktivieren", logger.WARNING);
                containerDetecor.running = False;
                
            freedom.stop();
                  
            freedom.setLedOff()
                     
except:
    print"BYE"
    containerDetecor.running = False;
    freedom.stop();
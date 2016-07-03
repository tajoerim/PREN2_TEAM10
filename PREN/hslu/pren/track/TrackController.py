'''
Created on 08.12.2015

@author: Christoph
'''

import xml.etree.ElementTree as ET
        
    
class TrackController():

    #Constructor
    def __init__(self, startPoint="B"):

        if (startPoint == 'a'):
            startPoint = 'A'

        if (startPoint == 'b'):
            startPoint = 'B'

        self.startPoint = startPoint
        try:
            tree = ET.parse('/home/pi/PREN/PROD/hslu/pren/track/track' + startPoint + '.xml')
        except:
            tree = ET.parse('C:/Users/Christoph/git/PREN/PREN/hslu/pren/track/track' + startPoint + '.xml')

        trackRoot = tree.getroot()
        self.locations = trackRoot.findall('Location')
        
    def getPositionEvent(self, position):
        '''
        Sucht das passende Event aus dem XML mit allen Positions-Events
        heraus und bildet daraus ein Location Objekt.
        
        @param startPoint: Startposition gem. Aufgabenstellung
        
        @return: Location Objekt mit auszufuehrender Action
        '''
        
        #return "crossingRoad"
        #return "checkContainer"
        #return "driveCurve"

        prevDist = 0
        distTo = 0

        if (position is not None):
            for location in self.locations:
                distFrom = prevDist
                distTo = prevDist + int(location.get('distance'))

                #if (location.get('id') == "14"):
                #    return "stop"

                if (distFrom <= int(position) and distTo >= int(position)):
                    return location.find('action').text

                prevDist = distTo

        return "handlePitLane"
        
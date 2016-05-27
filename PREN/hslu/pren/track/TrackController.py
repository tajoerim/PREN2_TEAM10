'''
Created on 08.12.2015

@author: Christoph
'''

import xml.etree.ElementTree as ET
        
    
class TrackController():

    #Constructor
    def __init__(self, startPoint="A"):
        self.startPoint = startPoint
        tree = ET.parse('/home/pi/PREN/PROD/hslu/pren/track/track.xml')
        trackRoot = tree.getroot()
        self.locations = trackRoot.findall('Location')
        
    def getPositionEvent(self, position):
        '''
        Sucht das passende Event aus dem XML mit allen Positions-Events
        heraus und bildet daraus ein Location Objekt.
        
        @param startPoint: Startposition gem. Aufgabenstellung
        
        @return: Location Objekt mit auszufuehrender Action
        '''
        prevDist = 0
        distTo = 0

        if (position is not None):
            for location in self.locations:
                distFrom = prevDist
                distTo = prevDist + int(location.get('distance'))

                if (distFrom <= int(position) and distTo >= int(position)):
                    return location.find('action').text

                prevDist = distTo

        return "driveCurve"
        
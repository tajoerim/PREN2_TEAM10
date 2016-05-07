'''
Created on 08.12.2015

@author: Christoph
'''

import xml.etree.ElementTree as ET
      
class Location():

    #Constructor
    def __init__(self, name, action, addInfo):
        self.name = name
        self.action = action
        self.addInfo = addInfo
        
    def __str__(self):
        print "Name:" + self.name + " Action: " + self.action + " Additional info: " + self.addInfo
        
    
class TrackController():

    #Constructor
    def __init__(self, startPoint="A"):
        self.startPoint = startPoint
        
    def getPositionEvent(self, position):
        '''
        Sucht das passende Event aus dem XML mit allen Positions-Events
        heraus und bildet daraus ein Location Objekt.
        
        @param startPoint: Startposition gem. Aufgabenstellung
        
        @return: Location Objekt mit auszufuehrender Action
        '''
        
        tree = ET.parse('hslu/pren/track/track.xml')
        trackRoot = tree.getroot()
        
        prevDist = 0
        for location in trackRoot.findall('Location'):
            distFrom = prevDist
            distTo = prevDist + int(location.get('distance'))
            
            if (distFrom <= position and distTo >= position):
                name = location.find('name').text
                action = location.find('action').text
                addInfo = ''
            
                loc = Location(name, action, addInfo)

                return loc

            prevDist = prevDist + distTo
        
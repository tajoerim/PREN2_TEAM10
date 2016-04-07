
from hslu.pren.communication import *

import threading
import sys
import time

class BatteryAgent(threading.Thread):

    INTERVAL_SECONDS = 3

    # Constructor
    def __init__(self, freedom, debug):
        threading.Thread.__init__(self)
        self.freedom = freedom
        self.debug = debug
        self.running = True
        self.batteryLow = 0

    def isBatteryLow(self):
        if (self.batteryLow == 0):
            return False
        return True

    def run(self):

        while (self.running):
            try:
                if (self.debug):
                    self.batteryLow = 0
                else:
                    self.batteryLow = self.freedom.isBatteryLow()
                    
            except KeyboardInterrupt:
                return

            time.sleep(self.INTERVAL_SECONDS) # Wir machen den check alle 3 Sekunden
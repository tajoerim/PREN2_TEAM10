﻿class Logger():

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, componentName):
        self.name = componentName

    def log(self, msg, color):
        print color + "[" + self.name + "] " + msg + self.ENDC
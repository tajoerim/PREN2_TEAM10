#!/usr/local/bin/python2.7
# encoding: utf-8
'''
hslu.pren.control.Main -- Controlling fuer autonomes Entsorgungsfahrzeug

@author:     Christoph Joerimann, Matthias Kafka (Team 10)

@copyright:  2015 Team 10 - HSLU, PREN HS15 & FS16. All rights reserved.

@license:    license

@contact:    christoph.joerimann@stud.hslu.ch
@deffield    updated: Updated
'''

import ptvsd

#ptvsd.enable_attach(secret='passwd')


import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from hslu.pren.control import Controller



__all__ = []
__version__ = 0.1
__date__ = '2015-12-08'
__updated__ = '2015-12-08'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Christoph Joerimann, Matthias Kafka (Team 10) on %s.
  Copyright 2015 Team 10 - HSLU, PREN HS15 & FS16. All rights reserved.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-b", "--blue", dest="blue", action="store_true", help="Container Farbe [[Blau], Gruen]")
        parser.add_argument("-g", "--green", dest="green", action="store_true", help="Container Farbe [[Blau], Gruen]")
        parser.add_argument("-pi", "--pi", dest="raspberry", action="store_true", help="is it Raspberry Pi?")
        parser.add_argument("-d", "--d", dest="debug", action="store_true", help="is it debug?")
        parser.add_argument("-x", "--x", dest="xVision", action="store_true", help="enable X11?")
        parser.add_argument("-wp", "--webcamPort", dest="webcamPort", action="store", help="webcam port")
        parser.add_argument("-fp", "--freedomPort", dest="freedomPort", action="store", help="freedom port")
        parser.add_argument("-s", "--startPoint", dest="startPoint", action="store", help="Start point (A or B)")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        blue = args.blue
        green = args.green

        if (args.raspberry):
            raspbbery = True
        else:
            raspbbery = False

        if (args.debug):
            debug = True
        else:
            debug = False 

        if (args.xVision):
            xVision = True
        else:
            xVision = False 

        if blue:
            print 'initialize blue color'
            ctrl = Controller.Controller('blue', args.webcamPort, args.freedomPort, args.startPoint, raspbbery, debug, xVision)
            ctrl.run()
        elif green:
            print 'initialize green color'
            ctrl = Controller.Controller('green', args.webcamPort, args.freedomPort, args.startPoint, args.raspberry, debug, xVision)
            ctrl.run()
        else:
            print 'unknown color argument'


        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        ctrl.stop()
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())
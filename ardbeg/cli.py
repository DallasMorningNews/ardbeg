#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""ardbeg

Usage:
  ardbeg develop [--port=<port>]
  ardbeg publish
  ardbeg init
  ardbeg (-h | --help) --pagepath=<pagepath>
  ardbeg --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
import os
import sys
from ardbeg import directoryCheck, argCheck, make_publisher, initialize, getSettings

def start():
    global docArgs
    docArgs = docopt(__doc__, version='ardbeg 0.0.1')
    
    #Must be run from root of project directory
    ROOT = os.getcwd()

    develop = docArgs['develop']
    publish = docArgs['publish']
    init = docArgs['init']

    if init:
    	initialize()
    else:
      getSettings()
      templatePath = argCheck('templatePath')
      staticPath = argCheck('staticPath')
      contentPath = argCheck('contentPath')
      outputPath = argCheck('outputPath')
      dataPath = argCheck('dataPath')

      if docArgs['--port'] == None:
          devPort = '4242'
      else:
          devPort = docArgs['--port']

      publisher = make_publisher(
	    templatePath = templatePath,
	    staticPath   = staticPath  ,
	    outputPath   = outputPath  ,
	    contentPath  = contentPath ,
	    dataPath     = dataPath    ,
      devPort      = devPort     ,
	    )

      publisher.run(develop=develop,publish=publish)


if __name__ == '__main__':
    start()
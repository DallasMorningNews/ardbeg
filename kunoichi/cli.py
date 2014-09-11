#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""kuniochi

Usage:
  kuniochi develop [--outputPath=<outputPath> --dataPath=<dataPath> --homePath=<homePath> --staticPath=<staticPath> --templatePath=<templatePath> --contentPath=<contentPath> ]
  kuniochi publish [--outputPath=<outputPath> --dataPath=<dataPath> --homePath=<homePath> --staticPath=<staticPath> --templatePath=<templatePath> --contentPath=<contentPath> ]
  kuniochi (-h | --help) --pagepath=<pagepath>
  kuniochi --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

from docopt import docopt
import os
import sys
from kunoichi import kunoichi

def start():
    arguments = docopt(__doc__, version='kunoichi 0.0.1')

    def argcheck(argString,default):
      if arguments[argString] is not None:
          direct = arguments[argString]
      else:
          direct = os.path.join(os.getcwd(),default)
      if not os.path.exists(direct):
          print("The directory '%s' is invalid."
                % direct)
          sys.exit(1)
      return direct

    #Defaults
    homePath = argcheck('--homePath','')
    templatePath   = argcheck('--templatePath','templates')
    staticPath = argcheck('--staticPath','static' )
    outputPath    = argcheck('--outputPath','rendered' )
    contentPath   = argcheck('--contentPath','content'   )
    dataPath   = argcheck('--dataPath','data'   )


    publisher = kunoichi.make_publisher(
        homePath     = homePath    , 
    templatePath = templatePath,
    staticPath   = staticPath  ,
    outputPath   = outputPath  ,
    contentPath  = contentPath ,
    dataPath     = dataPath    ,
    )


    develop = arguments['develop']
    publish = arguments['publish']

    publisher.run(develop=develop,publish=publish)


if __name__ == '__main__':
    start()
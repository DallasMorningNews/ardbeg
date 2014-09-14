#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""ardbeg

Usage:
  ardbeg develop [--TempVersion=<TempVersion> --outputPath=<outputPath> --dataPath=<dataPath> --homePath=<homePath> --staticPath=<staticPath> --templatePath=<templatePath> --contentPath=<contentPath> ]
  ardbeg publish [--TempVersion=<TempVersion> --outputPath=<outputPath> --dataPath=<dataPath> --homePath=<homePath> --staticPath=<staticPath> --templatePath=<templatePath> --contentPath=<contentPath> ]
  ardbeg init [--TempVersion=<TempVersion>]
  ardbeg (-h | --help) --pagepath=<pagepath>
  ardbeg --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
import os
import sys
from ardbeg import directory_check, argCheck, make_publisher, initialize

def start():
    docArgs = docopt(__doc__, version='ardbeg 0.0.1')
    
    #Must be run from root of project directory
    ROOT = os.getcwd()

    develop = docArgs['develop']
    publish = docArgs['publish']
    init = docArgs['init']

    if init:
    	initialize()
    else:
	    homePath = ROOT
	    templatePath   = directory_check(argCheck(docArgs,'--templatePath','templates'))
	    staticPath = directory_check(argCheck(docArgs,'--staticPath','static' ))
	    outputPath    = directory_check(argCheck(docArgs,'--outputPath','rendered' ))
	    contentPath   = directory_check(argCheck(docArgs,'--contentPath','content'   ))
	    dataPath   = directory_check(argCheck(docArgs,'--dataPath','data'   ))


	    publisher = make_publisher(
	        homePath = homePath    , 
	    templatePath = templatePath,
	    staticPath   = staticPath  ,
	    outputPath   = outputPath  ,
	    contentPath  = contentPath ,
	    dataPath     = dataPath    ,
	    )

	    publisher.run(develop=develop,publish=publish)


if __name__ == '__main__':
    start()
#!/usr/bin/env python
import inspect
import logging
import os, os.path
import sys
import re
import shutil
from distutils.dir_util import copy_tree
import datetime
from jinja2 import Environment, FileSystemLoader, PrefixLoader
import table_fu

############################################################################################
### S3 Publish plus repo ###
############################

import boto, boto.s3
from boto.s3.connection import S3Connection

###########
# Connect #
###########

if not os.environ.get('AWS_ACCESS_KEY_ID') or not os.environ.get('AWS_SECRET_ACCESS_KEY'):
    S3access = raw_input('Enter your AWS access key ID: ')
    S3secret = raw_input('Enter your AWS secret access key: ')
    S3 = S3Connection(S3access, S3secret)
else:
    S3 = S3Connection()

if not os.environ.get('AWS_REPO_BUCKET') or not os.environ.get('AWS_PUBLISH_BUCKET'):
    S3Publish = raw_input('Enter name of AWS publishing bucket: ')
    S3Repo = raw_input('Enter name of AWS back-up repository bucket: ')
    PublishBucket = S3.get_bucket(S3Publish)
    RepoBucket = S3.get_bucket(S3Repo)
else:
    PublishBucket = S3.get_bucket(os.environ.get('AWS_PUBLISH_BUCKET'))
    RepoBucket = S3.get_bucket(os.environ.get('AWS_REPO_BUCKET'))

#############################################################################################


class publisher(object):
	def __init__(self,environment,homePath,staticPath,templatePath,contentPath,dataPath,outputPath,logger):
		self._env = environment
		self.homePath = homePath
		self.staticPath = staticPath
		self.templatePath = templatePath
		self.contentPath = contentPath
		self.outputPath = outputPath
		self.dataPath = dataPath
		self.logger = logger

	def run(self,publish=False,develop=False):
		self.copy_static(self)
		self.render_templates(self)
		if publish:
			now = datetime.datetime.now()
			destDir = str(now.year)+"-"+os.path.basename(self.homePath)
			upload(PublishBucket,outputPath,destDir)
			upload(RepoBucket,outputPath,destDir)
		if develop:
			pass

	def copy_static(self):
		staticWrite = os.path.join(self.outPath,os.path.basename(os.path.normpath(self.staticPath)))
		copy_tree(self.staticPath,staticWrite)

	def render_templates(self):
		#render index.html in project root first, if it exists
		try:
			template = self._env.get_template('content/index.html')
			self.logger.info("Rendering %s..." % template.name)
			dataContext = dataLoad(self)
			template.stream(dataContext).dump(os.path.join(self.outputPath,'index.html'))
		except Exception:
			pass
		#render content pages and write with any subdirectory structure
		#overwrites index.html if duplicate in contentPath
		for directory,subs,files in os.walk(self.contentPath):
			for file in files:
				template = self._env.get_template('content/'+file)
				self.logger.info("Rendering %s..." % template.name)
				dataContext = dataLoad(self)
				template.stream(dataContext).dump(os.path.join(self.outputPath,os.path.relpath(os.path.join(directory,file),self.contentPath)))

	def dataLoad(self):
		contexts={}
		for file in os.listdir(self.dataPath):
			table = table_fu.TableFu(open(file,'U'))
			contexts[ os.path.splitext(os.path.basename(file))[0] ] = table
		return contexts
		

class tinkerer(object):
	def __init__(self, publisher):
		self.publisher = publisher 


	def should_handle(self, event_type, filename):
	    print "%s %s" % (event_type, filename)
	    return (event_type == "modified"
	            and filename.startswith(self.searchpath))

	def event_handler(self, event_type, src_path):
	    filename = os.path.relpath(src_path, self.searchpath)
	    if self.should_handle(event_type, src_path):
	        if self.renderer.is_static(filename):
	            files = self.renderer.get_dependencies(filename)
	            self.renderer.copy_static(files)
	        else:
	            templates = self.renderer.get_dependencies(filename)
	            self.renderer.render_templates(templates)

	def watch(self):
	    import easywatch
	    easywatch.watch(self.searchpath, self.event_handler)

	def serve(self):
	    import SimpleHTTPServer
	    import SocketServer
	    os.chdir(self.outPath)
	    PORT = 4242
	    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
	    httpd = SocketServer.TCPServer(("", PORT), Handler)
	    httpd.serve_forever()

	def develop(self):
	    import threading
	    import time
	    watcher = threading.Thread(target=self.watch)
	    watcher.daemon = True
	    server = threading.Thread(target=self.serve)
	    server.daemon = True
	    server.start()
	    watcher.start()
	    while True:
	        time.sleep(1)


def make_publisher(homePath,
                  staticPath,
                  templatePath,
                  contentPath,
                  dataPath,
                  outputPath,
                  ):

    loader = PrefixLoader({
    		'template':FileSystemLoader(absoluteList(templatePath)),
    		'content' :FileSystemLoader(absoluteList(contentPath)+[absolutePath(homePath)])
    	})

    environment = Environment(loader=loader)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return publisher(environment,
                    homePath=homePath,      
                    staticPath = staticPath,
                    templatePath=templatePath,
                    contentPath=contentPath,
                    dataPath=dataPath,
                    outputPath=outputPath,
                    logger=logger,
                    )


##########################################################################################
## Helper Funcs ##
##################

def upload(bucket,sourceDir,destDir):
    k = boto.s3.key.Key(bucket)
    for path,dir,files in os.walk(sourceDir): 
        for file in files: 
        	abspath = os.path.join(path,file)
            relpath = os.path.relpath(abspath,sourceDir) 
            destpath = os.path.join(destDir, relpath)
            print 'Uploading %s to Amazon S3 bucket %s' % (relpath, bucket)
            k.key = destpath
            k.set_contents_from_filename(abspath)
            k.set_acl('public-read')
    print "Uploaded to AWS"

## Force absolute paths 
def absoluteList(path):
    if not os.path.isabs(path):
        project_path = os.getcwd()
        path = os.path.join(project_path, path)
    return [direct[0] for direct in os.walk(path)]

def absolutePath(path):
    if not os.path.isabs(path):
        project_path = os.getcwd()
        return os.path.join(project_path, path)
    return path

	


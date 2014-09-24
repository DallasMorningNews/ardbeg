#!/usr/bin/env python
import inspect
import logging
import os, os.path
import sys
import re
import shutil
from distutils.dir_util import copy_tree
import datetime
import zipfile
from jinja2 import Environment, FileSystemLoader, PrefixLoader
import table_fu
import webbrowser
import sass
import json
import traceback
from jinja_filters import func_list

ROOT = os.getcwd()

def getSettings():
	global SETTINGS
	try:
		SETTINGS = json.load(open(os.path.join(ROOT,'settings')))	
	except Exception:
		print "!#!#!# Settings file not found in project root! Add one. (see README)"
		sys.exit(1)

def jinjaEnv(templatePath,contentPath):
	loader = PrefixLoader({
    		'template':FileSystemLoader(absoluteList(templatePath)),
    		'content' :FileSystemLoader(absoluteList(contentPath)+[absolutePath(ROOT)])
    	})

	environment = Environment(loader=loader)
	for func in func_list:
		environment.filters[func.__name__]=func
	return environment

################
## Init funcs ##
################
'''
Init funcs need to be safe to run repeatedly on working directory in order to load templates 
after adding directory to settings.
'''
def initialize():
	print "<ardbeg> Making development directory."
	writeSettings()
	getSettings()
	directoryDefaultWriter()
	#dumb check for S3 creds
	if SETTINGS.get('AWS_ACCESS_KEY_ID',None) or os.environ.get('AWS_ACCESS_KEY_ID'):
		S3,PublishBucket,RepoBucket,TemplateBucket = S3wires()
		loadTemplates(TemplateBucket)
	else:
		print "<ardbeg> --No S3 template repo found. Can add bucket to settings and rerun ardbeg init."
	templateIndex(os.path.join(ROOT,SETTINGS.get('templatePath')))
	templateStatic( os.path.join(ROOT,SETTINGS.get('staticPath')) , os.path.join(ROOT,SETTINGS.get('templatePath')) )
	print "<ardbeg> Development directory ready."

def directoryDefaultWriter():
	directories = ['template','static','rendered','content','data']
	for d in directories:
		makeDirectory(os.path.join(ROOT,d))
	
def writeSettings():
	'''
	Write settings from default_settings if doesn't already exist.
	'''
	if not os.path.isfile(os.path.join(ROOT,'settings')):
		from default_settings import DEFAULTSETTINGS
		file = open(os.path.join(ROOT,"settings"), "w+")
		file.write(json.dumps(DEFAULTSETTINGS,sort_keys=True,separators=(',\n',':') ))
		file.close()

def templateIndex(templatePath):
	'''
	If no index.html in project root, write a blank one.
	Then check for index.html in loaded templates. If one exists, move to root unless 
	non-blank index.html already there.
	'''
	if not os.path.isfile(os.path.join(ROOT,'index.html')):
		with open(os.path.join(ROOT,"index.html"), "w+"): pass
	if open(os.path.join(ROOT,"index.html"), "r").read() == "":
		for path,subdirs,files in os.walk(templatePath):
			for file in files:
				if file.lower() == "index.html":
					readFile = open(os.path.join(path,file),"r+")
					copy = readFile.read()
					writeFile = open(os.path.join(ROOT,"index.html"),"w+")
					writeFile.write(copy)
					writeFile.close()
					readFile.close()
					os.remove(os.path.join(path,file))


def templateStatic(staticPath,templatePath):
	'''
	Check for static directory in loaded templates. If exists and staticPath in
	dev is empty, replace. Remove static directory.
	'''
	for path,subdirs,files in os.walk(templatePath):
		for subdir in subdirs:
			if subdir == 'static':
				#if empty directory, copy to staticPath
				if len(os.listdir(staticPath))==0: 
					print "<ardbeg> Copying static files"
					shutil.rmtree(staticPath)
					shutil.copytree(os.path.join(path,subdir),staticPath)
				else:
					print "<ardbeg> Files in static directory. Cannot copy from template."
				shutil.rmtree(os.path.join(path,subdir))


############################
### S3 publish functions ###
############################

import boto, boto.s3
from boto.s3.connection import S3Connection

#S3 variables must be set as either environment variables or in settings in the project root
def S3wires():
	try:
		S3access = SETTINGS.get('AWS_ACCESS_KEY_ID',None)     or os.environ.get('AWS_ACCESS_KEY_ID')
		S3secret = SETTINGS.get('AWS_SECRET_ACCESS_KEY',None) or os.environ.get('AWS_SECRET_ACCESS_KEY')
		S3 = S3Connection(S3access, S3secret)
	except:
		print "!#!#!# No or bad S3 credentials passed to Ardbeg. Add some to settings. (see README)"
		sys.exit(1)

	def getBucket(bucket):
		try:
			bucket = S3.get_bucket(SETTINGS.get(bucket,None) or os.environ.get(bucket))
		except:
			bucket = None
			print "<ardbeg> -- No %s S3 bucket found." % bucket
		return bucket
	PublishBucket = getBucket('AWS_PUBLISH_BUCKET')
	RepoBucket = getBucket('AWS_REPO_BUCKET')
	TemplateBucket = getBucket('AWS_TEMPLATE_BUCKET')
	return S3,PublishBucket,RepoBucket,TemplateBucket

def upload(bucket,sourceDir,destDir):
    k = boto.s3.key.Key(bucket)
    for path,dir,files in os.walk(sourceDir): 
        for file in files: 
        	abspath = os.path.join(path,file)
        	relpath = os.path.relpath(abspath,sourceDir)
        	destpath = os.path.join(destDir, relpath)
        	print '<ardbeg> Publishing %s to S3 bucket %s' % (relpath, bucket)
        	k.key = destpath
        	k.set_contents_from_filename(abspath)
        	k.set_acl('public-read')

def archive(bucket,sourceDir,destDir):
	k = boto.s3.key.Key(bucket)
	zf = zipfile.ZipFile("temp.zip", "w")
	for path,dir,files in os.walk(sourceDir):
		for file in files:
			if file != 'temp.zip':
				relpath = os.path.join(os.path.basename(ROOT),os.path.relpath(os.path.join(path,file),ROOT))
				zf.write(os.path.join(path,file),relpath,zipfile.ZIP_DEFLATED)
	zf.close()
	print '<ardbeg> Archiving %s in S3 bucket %s' % (sourceDir, bucket)
	now = datetime.datetime.now()
	k.key = destDir
	k.set_contents_from_filename('temp.zip')
	k.set_acl('public-read')
	os.remove('temp.zip')

def loadTemplates(TemplateBucket):
	if TemplateBucket:
		version = SETTINGS.get('templateVersion',None) or ''
		localDir = os.path.join(ROOT,SETTINGS.get('templatePath')+'/s3-templates/')
		recursiveDelete(localDir)
		makeDirectory(os.path.join(localDir,version))
		print "<ardbeg> Loading S3 templates "+version+"..."
		keys = TemplateBucket.list(prefix=version)
		for k in keys:
			keyString = str(k.key)
			if k.key.endswith('/'):
				#handle folders uploaded alone which have their own keys
				makeDirectory(os.path.join(localDir+keyString))
			else:
				#handle files and files prepended with path
				makeKeyPath(keyString,localDir)
				k.get_contents_to_filename(os.path.join(localDir+keyString))
		templateIndex(os.path.join(ROOT,SETTINGS.get('templatePath')))
		templateStatic( os.path.join(ROOT,SETTINGS.get('staticPath')) , os.path.join(ROOT,SETTINGS.get('templatePath')) )

def makeKeyPath(keyPath,makePath):
	'''
	Depending on how things are uploaded to S3, you can have a directory key
	for each folder	or just a file prepended with a full path, for which we 
	need to create the directory first. This does that.
	'''
	pathList = keyPath.split('/')
	if len(pathList)>1:
		for i in range(len(pathList)):
			makeDir = os.sep.join(pathList[:i])
			makeDirectory(os.path.join(makePath,makeDir))




#############################################################################################

class publisher(object):
	def __init__(self,environment,staticPath,templatePath,contentPath,dataPath,outputPath,devPort,logger):
		self._env = environment
		self.staticPath = staticPath
		self.templatePath = templatePath
		self.contentPath = contentPath
		self.outputPath = outputPath
		self.dataPath = dataPath
		self.devPort = devPort
		self.logger = logger

	def run(self,publish=False,develop=False):
		getSettings()
		if publish:
			S3,PublishBucket,RepoBucket,TemplateBucket = S3wires()
			destDir = str(datetime.datetime.now().year)+"/"+os.path.basename(ROOT)
			permission = raw_input("Upload project to '"+destDir+"' in S3 bucket? (Y/N): ")
			if permission.lower() != 'y':
				custom = raw_input('Enter custom directory name to upload project to or enter "X" to cancel: ') 
				if custom.lower() == 'x':
					print "Cancelled publish."
					sys.exit(1)
				else:
					destDir=custom
			#loadTemplates(TemplateBucket)
			#Have to reload jinja env after loading templates
			#self._env=jinjaEnv(self.templatePath,self.contentPath)
			self.renderTemplates()
			self.copyStatic()
			if PublishBucket:
				upload(PublishBucket,self.outputPath,destDir)
			if RepoBucket:
				archive(RepoBucket,ROOT,destDir)
			#SIP IT, DON'T TIP IT!
			savout = os.dup(1)
			os.close(1)
			os.open(os.devnull, os.O_RDWR)
			try:
			   webbrowser.open("https://www.youtube.com/watch?v=_6P_cFtOP2M")
			finally:
			   os.dup2(savout, 1)

		if develop:
			self.renderTemplates()
			self.copyStatic()
			self.logger.info("<ardbeg> Watching '%s' for changes..." % ROOT)
			self.logger.info("<ardbeg> Serving on port %s" % self.devPort)
			self.logger.info("<ardbeg> Press Ctrl+C to stop.")
			tinkerer(self).develop()

	def copyStatic(self):
		staticWrite = os.path.join(self.outputPath,os.path.basename(os.path.normpath(self.staticPath)))
		shutil.copytree(self.staticPath,staticWrite)
		sassCompiler(staticWrite)

	def renderTemplates(self):
		#render index.html in project root first, IF it exists
		recursiveDelete(self.outputPath)
		try:
			template = self._env.get_template('content/index.html')
			self.logger.info("<ardbeg> Rendering %s..." % template.name)
			dataContext = self.dataLoad()
			template.stream(dataContext).dump(os.path.join(self.outputPath,'index.html'))
		
			for file in os.listdir(self.contentPath):
				template = self._env.get_template('content/'+file)
				self.logger.info("<ardbeg> Rendering %s..." % template.name)
				dataContext = self.dataLoad()
				template.stream(dataContext).dump(os.path.join(self.outputPath,file))
		except Exception as e:
			exception_data = traceback.format_exc().splitlines()
			print "!#!#!# Error rendering templates:"
			for line in  exception_data[-3:]:
				print line

	def dataLoad(self):
		contexts={}
		for file in os.listdir(self.dataPath):
			table = table_fu.TableFu(open(os.path.join(self.dataPath,file),'U'))
			contexts[ os.path.splitext(os.path.basename(file))[0] ] = table
		return contexts
		

class tinkerer(object):
	def __init__(self, publisher):
		self.publisher = publisher 
		self.searchpath = ROOT

	def shouldHandle(self, event_type, filename):
		#check to make sure file isn't in rendered path/prevent recursion
		if os.path.relpath(filename,self.publisher.outputPath).startswith('..'):
		    return (event_type == "modified"
		            and filename.startswith(self.searchpath))

	def eventHandler(self, event_type, src_path):
		filename = os.path.relpath(src_path, self.searchpath)
		if self.shouldHandle(event_type, src_path):
			self.publisher.renderTemplates()
			self.publisher.copyStatic()

	def watch(self):
	    import easywatch
	    easywatch.watch(self.searchpath, self.eventHandler)

	def serve(self):
	    import SimpleHTTPServer
	    import SocketServer
	    os.chdir(self.publisher.outputPath)
	    PORT = int(self.publisher.devPort)
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

def make_publisher(staticPath,
                  templatePath,
                  contentPath,
                  dataPath,
                  outputPath,
                  devPort,
                  ):

    environment = jinjaEnv(templatePath,contentPath)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return publisher(environment,    
                    staticPath = absolutePath(staticPath),
                    templatePath=absolutePath(templatePath),
                    contentPath=absolutePath(contentPath),
                    dataPath=absolutePath(dataPath),
                    outputPath=absolutePath(outputPath),
                    devPort = devPort,
                    logger=logger,
                    )

##################
## Helper Funcs ##
##################

def recursiveDelete(delPath):
	for path,dirs,files in os.walk(delPath):
		for file in files: 
			os.remove(os.path.join(path,file))
	for path,dirs,files in os.walk(delPath):
		for dir in dirs:
			shutil.rmtree(os.path.join(path,dir))

def absolutePath(path):
	if not os.path.isabs(path):
		return os.path.join(ROOT, path)
	return path

def absoluteList(path):
	path=absolutePath(path)
	return [direct[0] for direct in os.walk(path)]

def argCheck(settingString):
	getSettings()
	try:
		variable = directoryCheck(SETTINGS[settingString])
	except:
		print "!#!#!# No directory provided for %s. Add one to settings."
		sys.exit(1)
	return variable

def directoryCheck(directory):
	if not os.path.isabs(directory):
		directory = os.path.join(ROOT,directory)
	if not os.path.exists(directory):
		print "!#!#!# The directory '%s' is invalid." % directory
		sys.exit(1)
	else:
		return directory

def makeDirectory(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def sassCompiler(directory):
	for root,dirs,files in os.walk(directory):
		for file in files:
			extension = os.path.splitext(file)[1][1:].strip().lower()
			if extension == "sass":
				with open (os.path.join(root,file), "r") as sassFile:
					string = sassFile.read().replace('\n','')
					cssFile = open(os.path.join(root,os.path.splitext(file)[0]+".css"),"w+")
					cssFile.write(sass.compile(string=string))
					cssFile.close()
				os.remove(os.path.join(root,file))
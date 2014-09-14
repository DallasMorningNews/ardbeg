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

ROOT = os.getcwd()

def get_settings():	
	global SETTINGS
	try:
		SETTINGS = {}
		execfile('settings.py',SETTINGS)
	except Exception:
		print "!#!#!# Settings file not found in project root! Add one. (see README)"
		sys.exit(1)

def jinja_env(templatePath,contentPath,homePath=None):
	loader = PrefixLoader({
    		'template':FileSystemLoader(absoluteList(templatePath)),
    		'content' :FileSystemLoader(absoluteList(contentPath)+[absolutePath(homePath)])
    	})
	return Environment(loader=loader)

################
## Init funcs ##
################
def initialize():
	print "<ardbeg> Making development directory."
	directoryDefaultWriter()
	#dumb check for S3 creds
	get_settings()
	if SETTINGS.get('AWS_TEMPLATE_BUCKET',None) or os.environ.get('AWS_TEMPLATE_BUCKET'):
		S3,PublishBucket,RepoBucket,TemplateBucket = S3wires()
		loadTemplates(TemplateBucket)
	else:
		print "<ardbeg> No S3 template repo found. Can add to setting.py and rerun ardbeg init."
	print "<ardbeg> Development directory ready."

def directoryDefaultWriter():
	directories = ['templates','static','rendered','content','data']
	for d in directories:
		makeDirect(os.path.join(ROOT,d))
	#Inelegant, this...
	if not os.path.isfile(os.path.join(ROOT,'index.html')):
		file = open(os.path.join(ROOT,"index.html"), "w+")
		file.write("{% \extends 'template/build.html'%}\n")
		file.close()
	if not os.path.isfile(os.path.join(ROOT,'settings.py')):
		from default_settings import DEFAULTSETTINGS
		file = open(os.path.join(ROOT,"settings.py"), "w+")
		for key in DEFAULTSETTINGS:
			if DEFAULTSETTINGS[key] =='None':
				file.write(key+"="+DEFAULTSETTINGS[key]+"\n")
			else:
				file.write(key+"='"+DEFAULTSETTINGS[key]+"'\n")
		file.close()

############################
### S3 Publish functions ###
############################

import boto, boto.s3
from boto.s3.connection import S3Connection

#S3 variables must be set as either environment variables or in settings.py in the project root
def S3wires():
	try:
		S3access = SETTINGS.get('AWS_ACCESS_KEY_ID',None)     or os.environ.get('AWS_ACCESS_KEY_ID')
		S3secret = SETTINGS.get('AWS_SECRET_ACCESS_KEY',None) or os.environ.get('AWS_SECRET_ACCESS_KEY')
		S3 = S3Connection(S3access, S3secret)
	except:
		print "!#!#!# No S3 credentials passed to Ardbeg. Add some to settings.py. (see README)"
		sys.exit(1)

	def get_bucket(bucket):
		try:
			bucket = S3.get_bucket(SETTINGS.get(bucket,None) or os.environ.get(bucket))
		except:
			bucket = None
		return bucket
	PublishBucket = get_bucket('AWS_PUBLISH_BUCKET')
	RepoBucket = get_bucket('AWS_REPO_BUCKET')
	TemplateBucket = get_bucket('AWS_TEMPLATE_BUCKET')
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
	k.key = str(now.year)+"/"+os.path.basename(sourceDir)
	k.set_contents_from_filename('temp.zip')
	k.set_acl('public-read')
	os.remove('temp.zip')

def loadTemplates(TemplateBucket):
	if TemplateBucket:
		version = SETTINGS.get('TempVersion',None) or argCheck(docArgs,'--TempVersion')
		localDir = os.path.join(ROOT,'templates/s3-templates/')
		recursive_delete(localDir)
		makeDirect(os.path.join(localDir,version))
		print "<ardbeg> Downloading S3 templates "+version
		keys = TemplateBucket.list(prefix=version)
		for k in keys:
			#avoiding directory keys in a dumb way...
			if not k.key.endswith('/'):
				keyString = str(k.key)
				k.get_contents_to_filename(os.path.join(localDir+keyString))

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
		get_settings()
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
			loadTemplates(TemplateBucket)
			#reload jinja env after loading templates
			self._env=jinja_env(self.templatePath,self.contentPath,self.homePath)
			self.render_templates()
			self.copy_static()
			if PublishBucket:
				upload(PublishBucket,self.outputPath,destDir)
			if RepoBucket:
				archive(RepoBucket,ROOT,destDir)
			savout = os.dup(1)
			os.close(1)
			os.open(os.devnull, os.O_RDWR)
			try:
			   webbrowser.open("https://www.youtube.com/watch?v=_6P_cFtOP2M")
			finally:
			   os.dup2(savout, 1)

		if develop:
			self.render_templates()
			self.copy_static()
			self.logger.info("<ardbeg> Watching '%s' for changes..." % ROOT)
			self.logger.info("<ardbeg> Serving on port 4242")
			self.logger.info("<ardbeg> Press Ctrl+C to stop.")
			tinkerer(self).develop()

	def copy_static(self):
		staticWrite = os.path.join(self.outputPath,os.path.basename(os.path.normpath(self.staticPath)))
		shutil.copytree(self.staticPath,staticWrite)
		sassCompiler(staticWrite)

	def render_templates(self):
		#render index.html in project root first, IF it exists
		recursive_delete(self.outputPath)
		try:
			template = self._env.get_template('content/index.html')
			self.logger.info("<ardbeg> Rendering %s..." % template.name)
			dataContext = self.dataLoad()
			template.stream(dataContext).dump(os.path.join(self.outputPath,'index.html'))
		except Exception:
			pass

		for file in os.listdir(self.contentPath):
			template = self._env.get_template('content/'+file)
			self.logger.info("<ardbeg> Rendering %s..." % template.name)
			dataContext = self.dataLoad()
			template.stream(dataContext).dump(os.path.join(self.outputPath,file))

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

	def should_handle(self, event_type, filename):
		#check to make sure file isn't in rendered path/prevent recursion
		if os.path.relpath(filename,self.publisher.outputPath).startswith('..'):
		    return (event_type == "modified"
		            and filename.startswith(self.searchpath))

	def event_handler(self, event_type, src_path):
		filename = os.path.relpath(src_path, self.searchpath)
		if self.should_handle(event_type, src_path):
			self.publisher.render_templates()
			self.publisher.copy_static()

	def watch(self):
	    import easywatch
	    easywatch.watch(self.searchpath, self.event_handler)

	def serve(self):
	    import SimpleHTTPServer
	    import SocketServer
	    os.chdir(self.publisher.outputPath)
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

    environment = jinja_env(templatePath,contentPath,homePath)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return publisher(environment,
                    homePath=absolutePath(homePath),      
                    staticPath = absolutePath(staticPath),
                    templatePath=absolutePath(templatePath),
                    contentPath=absolutePath(contentPath),
                    dataPath=absolutePath(dataPath),
                    outputPath=absolutePath(outputPath),
                    logger=logger,
                    )

##################
## Helper Funcs ##
##################

def recursive_delete(delPath):
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

def argCheck(docArgs, docString, default=None):
	'''
	Checks for value in this heirarchy: console argument > settings variable > default (passed) > None.
	'''
	get_settings()
	settingString = docString.replace('--','')
	if docArgs[docString] is not None:
		variable = docArgs[docString]
	elif SETTINGS.has_key(settingString) and SETTINGS[settingString] is not None:
		variable = SETTINGS[settingString]
	elif default is not None:
		variable = default
	else:
		variable = None
	return variable

def directory_check(directory):
	if not os.path.isabs(directory):
		directory = os.path.join(ROOT,directory)
	if not os.path.exists(directory):
		print "!#!#!# The directory '%s' is invalid." % directory
		sys.exit(1)
	else:
		return directory

def makeDirect(directory):
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
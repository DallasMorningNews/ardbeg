from collections import OrderedDict

defaults = {
'tempVersion  		   ': "",
'homePath     		   ': "", 
'templatePath 		   ': "templates", 
'staticPath   		   ': "static", 
'outputPath   		   ': "rendered", 
'contentPath  		   ': "content", 
'dataPath     		   ': "data", 
'AWS_ACCESS_KEY_ID     ':'None',
'AWS_SECRET_ACCESS_KEY ':'None',
'AWS_REPO_BUCKET       ':'None',
'AWS_PUBLISH_BUCKET    ':'None',
}

DEFAULTSETTINGS = OrderedDict(sorted(defaults.items(), key=lambda t: t[0]))
![ardbeg](/img/ardbeg.jpg)
========

Ardbeg is one crotchety python static site generator. It uses Jinja2 to renderer templates and publishes your static site to an Amazon Web Services S3 bucket.

But Ardbeg likes things done a certain way. It insists on a distributed directory development environment. Why distributed? Because at _The Dallas Morning News_ we take our Ardbeg neat and opinionated. 

Ardbeg is designed for the way we work, one project at a time, usually isolated.  

##Installation
```pip install ardbeg```

##Ardbeg has opinions.

###Directories
Ardbeg insists on a certain directory structure for your projects.
```

|--project/
|  |--<index.html>
|  |--templates/
|  |--content/
|  |--static/
|  |--data/
|  |--rendered/

```
- **templates** - Ardbeg will recursively search this directory for templates and partials to render content with.
- **content** - Flat directory of content html pages. Alternatively you may have an index.html in the root of the project. 
- **static** - Ardbeg simply copies this directory to the rendered directory, wholesale, because Ardbeg just don't give a damn.
- **data** - Put CSV files with structured data in this directory, and Ardbeg will expose the data in your templates' context.
- **rendered** - Output directory Ardbeg renders templates to.


###Develop
`ardbeg develop` will render your templates and startup a python SimpleHTTPServer in the rendered directory on localhost:4242. It will also watch for any changes you make in the directory and re-render your templates on save.

###Publish
Ardbeg can pushing your site to an Amazon S3 bucket.

S3 settings are usually exposed through environment variables.

Ardbeg looks for:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_PUBLISH_BUCKET
- AWS_REPO_BUCKET

`ardbeg publish` will upload your rendered site to S3 under a key directory based on your outer project folder name prepended with the current year.

-----------------

- **Nose:** A ridge of vanilla leads to mountain of peat capped with citrus fruits and circled by clouds of sea spray.
- **Palate:** Sweet vanilla counterbalanced with lemon and lime followed by that surging Ardbeg smoke that we all know and love.
- **Finish:** Long and glorious; sea salted caramel and beach bonfire smoke.
- **Overall:** Precise balance, big smoke and non-chill filtered. This is why this is such a famous dram.




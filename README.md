![ardbeg](img/ardbeg.jpg)
========

Ardbeg is a Jinja2-based very simple static site renderer and publisher that depends on a distributed development directory environment. Why distributed? Because at _The Dallas Morning News_ we like our Ardbeg neat. 

##Installation
```pip install ardbeg```

##Usage

###Setup
Create a projects directory with the following subdirectories:

- templates
- static
- content
- data
- rendered
- you can also have a index.html in the root of your project

###Develop
`ardbeg develop` will render your templates and start up a python SimpleHTTPServer in the rendered directory on localhost:4242. It will also watch for any changes you make in the directory and re-render your templates on save.

###Publish
Ardbeg comes with code for pushing your site to an Amazon S3 bucket.






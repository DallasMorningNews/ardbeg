![ardbeg](/img/ardbeg.jpg)
========

Ardbeg is a python static site generator. It uses Jinja2 to renderer templates and publishes your static site to an Amazon Web Services S3 bucket.

But Ardbeg likes things done a certain way. It insists on a distributed directory development environment. Why distributed? Because at _The Dallas Morning News_ we take our Ardbeg neat and opinionated.

Ardbeg is designed for the way we work, one story at a time.

##Installation
```pip install ardbeg```

##Ardbeg has opinions.

###Directories
Ardbeg insists on a certain directory structure for your projects.

Luckily Ardbeg makes creating it easy. 

Run `ardbeg init` in an empty directory (ie, the project root, where all Ardbeg commands should be run from...). Ardbeg creates the following directory tree: 
```
|--project/
|  |--index.html
|  |--settings.py
|  |--templates/
|  |--content/
|  |--static/
|  |--data/
|  |--rendered/
```
- **templates/** - Ardbeg will recursively search this directory for templates and partials to render content with. You may have any nested directory structure in this folder, but all templates found by Jinja will be exposed as `templates/<template name>`. That means a flat namespace, so mind contradictions.
- **content/** - A flat directory of content html pages to render with templates. Alternatively you may use the `index.html` in the root of the project. Content is exposed as `content/<page name>`.
- **static/** - Ardbeg simply copies this directory to the rendered directory, wholesale. Use relative references to these files in your templates. Ardbeg also automatically compiles any files in this folder with the extension `.sass` from SASS files into CSS.
- **data/** - Put CSV files with structured data in this directory, and Ardbeg will expose the data in your templates' context. For example, if you put `people.csv` in this directory (with a header row), it's data can be used in your template like this:
```
{%for row in people.rows%}
<h4>{{row.FirstName}} {{row.LastName}}</h4>
{%endfor%}
```
- **rendered/** - Output directory where Ardbeg renders content and copies your static files.

Alternatively, you may set the locations of these directories through console options, settings.py or environment variables. The relevant variables are:

- `homePath` (the project root)
- `templatePath`
- `contentPath`
- `staticPath`
- `dataPath`
- `outputPath`

**NOTE:** Ardbeg insists a `settings.py` live in the root directory of your project. It does *not* insist that file actually contains any settings...

###Develop
`ardbeg develop` will render your templates and startup a Python SimpleHTTPServer in the rendered directory on [localhost:4242](http://localhost:4242). It will also watch for any changes you make in the project directory and automatically re-render your templates on save.

###Publish
Ardbeg can publish your site to an Amazon S3 bucket.

S3 settings are usually exposed through environment variables, but you may also set them in `settings.py`.

Ardbeg uses these variables:

- `AWS_ACCESS_KEY_ID` 
- `AWS_SECRET_ACCESS_KEY` 
- `AWS_PUBLISH_BUCKET` 
- `AWS_REPO_BUCKET` optional. If specified, Ardbeg will zip up your project folder from the root and deposit it here for safekeeping. 

`ardbeg publish` will upload your rendered site to S3 under a key directory based on your outer project folder name prepended with the current year, though you may set a custom directory name through console prompts.

You may also use an S3 bucket to store templates you frequently use to render content pages.

Set `AWS_TEMPLATE_BUCKET` environment variable or in `settings.py`. Optionally, set `TempVersion` in `settings.py` or pass via console option to download only templates in a certain directory of your S3 bucket.

Templates are downloaded to the templates directory under a sub-directory `s3-templates/` whenever you run `ardbeg init` and also on `ardbeg publish` before rendering your site. 

**Note:** The `s3-templates/` directory is scotched every time S3 templates are loaded and a fresh install pulled down. So put your custom, site specific templates outside this directory. 

Enter `ardbeg --help` for a list of available console commands.

-----------------
##Ardbeg apps taste like
- **Nose:** A ridge of vanilla leads to mountain of peat capped with citrus fruits and circled by clouds of sea spray.
- **Palate:** Sweet vanilla counterbalanced with lemon and lime followed by that surging Ardbeg smoke that we all know and love.
- **Finish:** Long and glorious; sea salted caramel and beach bonfire smoke.
- **Overall:** Precise balance, big smoke and non-chill filtered. This is why this is such a famous dram.




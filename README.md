![ardbeg](/img/ardbeg.jpg)
========

Ardbeg is a python static site generator. It uses Jinja2 to renderer templates and publishes your static site to an Amazon Web Services S3 bucket.

But Ardbeg likes things done a certain way. It insists on a distributed directory development environment. Why distributed? Because at _The Dallas Morning News_ we take our Ardbeg neat and opinionated.

#Features
- Ardbeg uses Jinja2 templates. They are [powerful](http://jinja.pocoo.org/docs/dev/templates/).
- Designed for a fully integrated AWS S3 workflow:
    - Load templates stored in S3 and maintain starter files you use regularly
    - Easily publish to an S3 bucket for static site hosting
    - Zip up your working directory and post it to an S3 archive, saving your work exactly as you left it without maintaining files locally.
- Creates a structured development directory for you and, with S3 hook-ups, loads in all your default templates and static files.
- Ardbeg's develop mode watches your working files and re-renders your site as you make changes.
- Ardbeg compiles your SASS files into CSS.
- Ardbeg makes it easy to create data-rich content in your pages by rendering structured data from CSV files in your template context.

As a Python shop, we think of Ardbeg as Django-lite: the best features of a web framework distilled into a small, highly-portable package. Ardbeg is written in Python for people who don't work in Python. Our designers use it to create stories with rich, interactive content outside our regular CMS.

##Installation
```pip install ardbeg```

##Ardbeg functions

- `ardbeg init`
- `ardbeg develop --port`
- `ardbeg publish`


###Init / development environment
Ardbeg insists on a certain directory structure for your projects.

Luckily, Ardbeg makes creating it easy. 

Run `ardbeg init` in an empty directory (i.e., the project root, where all Ardbeg commands should be run). Ardbeg creates the following directory tree: 
```
|--project/
|  |--index.html
|  |--settings
|  |--template/
|  |--content/
|  |--static/
|  |--data/
|  |--rendered/
```
- **index.html** - Default page to be rendered by Ardbeg.
- **settings** - A JSON file of available config variables for S3 and the development directory. The following are available:
    - `templatePath`
    - `contentPath`
    - `staticPath`
    - `dataPath`
    - `outputPath`
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`
    - `AWS_PUBLISH_BUCKET`
    - `AWS_REPO_BUCKET`
    - `AWS_TEMPLATE_BUCKET`
    - `templateVersion`
    
- **template/** - Ardbeg will recursively search this directory for templates and partials to render content with. You may have any nested directory structure in this folder, but all templates found by Jinja will be exposed as `template/<template name>`. That means a flat namespace, so mind contradictions.
    - **You can also** specify default static files and a default html page in this directory. Both are especially useful if loading templates from S3 (see Publish):
        - On `ardbeg init` if an `index.html` exists anywhere in `template/`, it is moved to the root of your project _unless a non-blank `index.html` is already there._
        - If Ardbeg finds a directory called static files, it is moved to the `staticPath` directory, _unless that directory is not empty._
        
- **content/** - A flat directory of content html pages to render with templates. Alternatively you may use the `index.html` in the root of the project. Content is exposed as `content/<page name>`.
- **static/** - Ardbeg simply copies this directory to the rendered directory, wholesale. Use relative references to these files in your templates. Ardbeg also automatically compiles any files in this folder with the extension `.sass` from SASS files into CSS.
- **data/** - Put CSV files with structured data in this directory, and Ardbeg will expose the data in your templates' context. For example, if you put `people.csv` in this directory (with a header row), it's data can be used in your template like this:
```
{%for row in people.rows%}
<h4>{{row.FirstName}} {{row.LastName}}</h4>
{%endfor%}
```
- **rendered/** - Output directory where Ardbeg renders content and copies your static files.

Alternatively, you may set the locations of these directories through the `settings` '...Path' variables.

**NOTE:** Ardbeg insists a `settings` file live in the root directory of your project. It does *not* insist that file actually contain any settings...

**SAFE CODING:**
`ardbeg init` is designed to be safely run anytime during development. Ardbeg checks to make sure directories are empty and files blank before it writes anything to your development directory. So for example, if you need to load S3 templates midway through a project, simply add S3 credentials to `settings` and re-run `ardbeg init`. The templates load into a directory `s3-templates/` but static files and index.html won't be written if these are non-empty in your development environment.

###Develop
`ardbeg develop` will render your templates and startup a Python SimpleHTTPServer in the rendered directory on [localhost:4242](http://localhost:4242) or whatever port you specify with `--port`. 

In develop, Ardbeg also watches for any changes you make in the project directory and automatically re-renders your templates whenever you save a file.

###Publish
Ardbeg can publish your site to an Amazon S3 bucket.

S3 settings are best handled by environment variables, but you may also set them in `settings`.

Ardbeg uses these variables:

- `AWS_ACCESS_KEY_ID` 
- `AWS_SECRET_ACCESS_KEY` 
- `AWS_PUBLISH_BUCKET` 
- `AWS_REPO_BUCKET` optional. If specified, Ardbeg will zip up your project folder from the root and deposit it here for safekeeping.

`ardbeg publish` will upload your rendered site to S3 under a key directory based on your outer project folder name prepended with the current year, though you may set a custom directory name through console prompts.

You may also use an S3 bucket to store templates you frequently use to render content pages. Set `AWS_TEMPLATE_BUCKET` environment variable or in `settings`. Optionally, set `templateVersion` in `settings` to download only templates in a certain directory of your S3 bucket.

Templates are downloaded to the templates directory under a sub-directory `s3-templates/` whenever you run `ardbeg init` or `ardbeg publish` before rendering your site. 

**Note:** The `s3-templates/` directory is scotched every time S3 templates are loaded and a fresh install pulled down. So put your custom, site-specific templates outside this directory.

##Credits:
- `Jinja2`
- `easywatch`
- `python-tablefu`
- `docopt`
- `boto`
- `libsass`
- `staticjinja` - *From whom we stole this idea and some code...*

-----------------
##Ardbeg static sites like
- **Nose:** A ridge of vanilla leads to mountain of peat capped with citrus fruits and circled by clouds of sea spray.
- **Palate:** Sweet vanilla counterbalanced with lemon and lime followed by that surging Ardbeg smoke that we all know and love.
- **Finish:** Long and glorious; sea salted caramel and beach bonfire smoke.
- **Overall:** Precise balance, big smoke and non-chill filtered. This is why this is such a famous dram.
from distutils.core import setup

setup(
    name='something-that-isnt-japanese',
    version='0.1.2',
    author='Jon McClure',
    author_email='jmcclure@dallasnews.com',
    packages=['kunoichi', 'kunoichi.test'],
    scripts=['bin/whitebelt','bin/blackbelt'],
    url='http://pypi.python.org/pypi/kunoichi/',
    license='LICENSE.txt',
    description='Static site generator based on Jinja2.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Jinja2 >= 2.7.3",
    ],
)

from distutils.core import setup

setup(
    name='kunoichi',
    version='0.1.1',
    author='Daniel Lathrop',
    author_email='dlathrop@dallasnews.com',
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
from setuptools import setup

setup(
    name='kunoichi',
    version='0.0.1',
    author='Jon McClure',
    author_email='jmcclure@dallasnews.com',
    packages=['kunoichi', 'kunoichi.test'],
    entry_points={
        'console_scripts': [
            'kunoichi = kunoichi.cli:start',
        ],
    },
    url='http://pypi.python.org/pypi/kunoichi/',
    license='LICENSE.txt',
    description='Static site generator based on Jinja2.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Jinja2 >= 2.7.3",
        "docopt",
        "easywatch",
        "python-tablefu",
        "boto",
    ],
)

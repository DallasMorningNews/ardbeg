from setuptools import setup

setup(
    name='ardbeg',
    version='0.0.1',
    author='Jon McClure',
    author_email='jmcclure@dallasnews.com',
    packages=['ardbeg', 'ardbeg.test'],
    entry_points={
        'console_scripts': [
            'ardbeg = ardbeg.cli:start',
        ],
    },
    url='http://pypi.python.org/pypi/ardbeg/',
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

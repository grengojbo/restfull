# -*- mode: python; coding: utf-8; -*-
from setuptools import setup, find_packages
import os, os.path
import sys

DIRNAME = os.path.dirname(__file__)

# Dynamically calculate the version based on django.VERSION.
version = "0.1.0"

setup(name='restfull',
    version=version,
    description="A REST client providing a convenience wrapper over httplib2",
    long_description="A REST Client for use in python, using httplib2 and urllib2. Includes a version that is suitable for use in the Google App Engine environment.",
    keywords='rest httplib3 urllib2',
    author='Oleg Dolya',
    author_email='oleg.dolya@gmail.com',
    url='http://github.com/grengojbo/restfull/',
    license='GPL',
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    #packages = packages,
    #data_files = data_files,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Topic :: Office/Business',
    ],
)

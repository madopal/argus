#!/usr/bin/env python

from setuptools import setup, find_packages

setup(  name='argus',
        version='0.0.1',
        description='Script to check on CTA routes',
        author='Joe Sislow',
        author_email='arslogic@madopal.com',
        py_modules=[],
        packages=find_packages(),
        install_requires=[
            'requests==2.7.0', 
            'xlwt',
            'lxml',
            'simplejson',
            'PyYAML==3.11',
            'gspread',
        ],
)


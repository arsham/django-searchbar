# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read_file(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-searchbar',
    version=__import__('django_searchbar').__version__,
    description="Simple searchbar and handler you can use in all your views and templates.",
    long_description=read_file('README.md'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Environment :: Web Environment',
    ],
    keywords=['searchbar', 'django', 'forms', 'template'],
    platforms=['OS Independen'],
    author='Arsham Shirvani',
    author_email='arshamshirvani@gmail.com',
    url='http://github.com/arsham/django-searchbar',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
)

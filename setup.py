# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read_file(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-search',
    version=__import__('django_search').__version__,
    description="Per-object judgment for Django, let them fight over permissions",
    long_description=read_file('README.md'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Security',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Environment :: Web Environment',
    ],
    keywords=['search', 'django', 'forms', 'template'],
    author='Arsham Shirvani',
    author_email='arshamshirvani@gmail.com',
    url='http://github.com/arsham/django-search',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
)

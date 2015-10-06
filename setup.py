#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='thriftrw',
    version='0.3.3',
    description=(
        'A library to serialize and deserialize Thrift values.'
    ),
    long_description=long_description,
    author='Abhinav Gupta',
    author_email='abg@uber.com',
    url='https://github.com/uber/thriftrw-python',
    packages=find_packages(exclude=('tests', 'tests.*')),
    license='MIT',
    install_requires=['six', 'ply'],
    tests_require=['pytest', 'mock'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

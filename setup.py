#!/usr/bin/env python

from setuptools import setup, find_packages

extra = {}

try:
    import Cython.Build
    # cython didn't support "from __future__" statements until 0.17.
    if tuple(int(v) for v in Cython.__version__.split('.')) > (0, 17, 0):
        extra = {
            'ext_modules': Cython.Build.cythonize([
                'thriftrw/protocol/binary.py',
                'thriftrw/wire/value.py',
                'thriftrw/spec/*.py',
            ]),
        }
except ImportError:
    pass

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='thriftrw',
    version='0.4.1.dev0',
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
    ],
    **extra
)

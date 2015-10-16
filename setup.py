#!/usr/bin/env python

import glob
from setuptools import setup
from setuptools import find_packages
from setuptools.extension import Extension
from setuptools.command.sdist import sdist as _sdist

cmdclass = {}
ext_modules = []

# If cython is available we will re-build our C extensions, otherwise we just
# compile the packaged C files.
try:
    import Cython.Distutils
    # cython didn't support "from __future__" statements until 0.17.
    if tuple(int(v) for v in Cython.__version__.split('.')) > (0, 17, 0):
        extension_filetype = '.pyx'
        cmdclass.update(build_ext=Cython.Distutils.build_ext)
except ImportError:
    extension_filetype = '.c'

for compiled_module in glob.glob('thriftrw/*/*.pyx'):
    ext_modules.extend([
        Extension(
            compiled_module.replace('/', '.')[:-4],
            [compiled_module.replace('.pyx', extension_filetype)]),
    ])


class sdist(_sdist):
    """This forces us to always re-compile extensions before releasing."""
    def run(self):
        try:
            from Cython.Build import cythonize
            cythonize(['thriftrw/*/*.pyx'])
        except ImportError:
            pass
        _sdist.run(self)

cmdclass['sdist'] = sdist


with open('README.rst') as f:
    long_description = f.read()

setup(
    name='thriftrw',
    version='0.5.2.dev0',
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
    ext_modules=ext_modules,
    cmdclass=cmdclass,
)

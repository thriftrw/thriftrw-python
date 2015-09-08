#!/usr/bin/env python

import os

from setuptools import setup
from setuptools import find_packages
from setuptools.extension import Extension
from setuptools.command.sdist import sdist as _sdist

cmdclass = {}
ext_modules = []

cython_modules = [
    'thriftrw._buffer',
    'thriftrw._cython',
    'thriftrw._runtime',
    'thriftrw.protocol.core',
    'thriftrw.protocol.binary',
    'thriftrw.spec.base',
    'thriftrw.spec.common',
    'thriftrw.spec.enum',
    'thriftrw.spec.exc',
    'thriftrw.spec.list',
    'thriftrw.spec.map',
    'thriftrw.spec.primitive',
    'thriftrw.spec.service',
    'thriftrw.spec.set',
    'thriftrw.spec.spec_mapper',
    'thriftrw.spec.struct',
    'thriftrw.spec.typedef',
    'thriftrw.spec.union',
    'thriftrw.wire.message',
    'thriftrw.wire.mtype',
    'thriftrw.wire.ttype',
    'thriftrw.wire.value',
]

# If Cython is available we will re-cythonize the pyx files, otherwise we just
# compile the packaged C files.
extension_filetype = '.c'
try:
    import Cython.Distutils

    # from __future__ import absolute_import needs cython >= 0.17
    if tuple(int(v) for v in Cython.__version__.split('.')) >= (0, 17, 0):
        cmdclass.update(build_ext=Cython.Distutils.build_ext)

        # Check if we forgot to add something to cython_modules.
        for root, _, files in os.walk('thriftrw'):
            for name in files:
                if not name.endswith('.pyx'):
                    continue
                path = os.path.join(root, name)
                module = path.replace('/', '.')[:-4]
                if module not in cython_modules:
                    raise Exception(
                        'Module "%s" (%s) is not present in the '
                        '"cython_modules" list.'
                        % (module, path)
                    )

        extension_filetype = '.pyx'
except ImportError:
    pass


for module in cython_modules:
    ext_modules.append(
        Extension(
            module,
            [module.replace('.', '/') + extension_filetype]
        )
    )


class sdist(_sdist):
    """This forces us to always re-compile extensions before releasing."""

    def run(self):
        try:
            from Cython.Build import cythonize

            cythonize([
                module.replace('.', '/') + '.pyx' for module in cython_modules
            ])
        except ImportError:
            pass
        _sdist.run(self)

cmdclass['sdist'] = sdist


with open('README.rst') as f:
    long_description = f.read()

setup(
    name='thriftrw',
    version='0.5.3.dev0',
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

import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
PY2 = sys.version_info[0] == 2

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as f:
    CHANGELOG = f.read()


REQUIREMENTS = [
    'waitress',
    'cliquet[monitoring]',
    'hkdf',
    'PyNaCl',
    'syncclient',
]

if PY2:
    REQUIREMENTS += [
        'pyopenssl',
        'ndg-httpsclient',
        'pyasn1'
    ]

ENTRY_POINTS = {
    'paste.app_factory': [
        'main = syncto:main',
    ]}

setup(name='syncto',
      version='1.4.0.dev0',
      description='Read Firefox Sync server using Kinto API.',
      long_description=README + "\n\n" + CHANGELOG,
      license='Apache License (2.0)',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: Implementation :: CPython",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "License :: OSI Approved :: Apache Software License"
      ],
      keywords="web services",
      author='Mozilla Services',
      author_email='services-dev@mozilla.com',
      url='https://syncto.readthedocs.org/',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      entry_points=ENTRY_POINTS)

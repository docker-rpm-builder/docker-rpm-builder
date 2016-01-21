import sys

from setuptools import setup, find_packages
from os.path import dirname, join

# this smells, but I don't know how to do better than this right now.
# let's remove all kind of whitespace/newline everywhere
VERSION=open(join(dirname(__file__), "version.txt")).read().replace(" ", "").replace("\n", "")

install_requires = [
    'Click==6.2',
    'unittest2 == 0.8.0',
    'setuptools == 12.0.5',
    'tzlocal == 1.2',
    'pytz == 2015.7'
]

if sys.version_info[1] == 6:
    install_requires.append("importlib")

setup(
    name='docker-rpm-builder',
    description="Fast native RPM building from any distro, for any distro, via docker",
    long_description=open("README.rst").read(),
    author="Alan Franzoni",
    author_email="username@franzoni.eu",
    url="https://github.com/alanfranz/docker-rpm-builder",
    version=VERSION,
    packages=find_packages(),
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        docker-rpm-builder=drb.cmdline:cmdline
    ''',
    license="Apache-2.0",
    include_package_data=True,
    zip_safe=False

)

import sys

from setuptools import setup, find_packages
from os.path import dirname, join

# this smells, but I don't know how to do better than this right now.
VERSION=open(join(dirname(__file__), "version.txt")).read().strip()

install_requires = [
    'Click==3.3',
    'unittest2 == 0.8.0',
    'setuptools == 12.0.5'
]

if sys.version_info[1] == 6:
    install_requires.append("importlib")

setup(
    name='docker-rpm-builder',
    description="Build native RPMs through docker",
    long_description=open("README.md").read(),
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
    setup_requires = ["setuptools_git == 1.1" ],
    license="Apache-2.0",
    include_package_data=True,
    zip_safe=False

)

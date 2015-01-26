import sys

from setuptools import setup, find_packages


install_requires = [
    'Click==3.3'
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
    version='2.0.dev',
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

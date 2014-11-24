from setuptools import setup, find_packages

setup(
    name='drb',
    version='1.0a1',
    packages=find_packages(),
    install_requires=[
        'Click==3.3',
    ],
    entry_points='''
        [console_scripts]
        drb=drb.cmdline:cmdline
    ''',
)
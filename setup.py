from setuptools import setup, find_packages

setup(
    name='drb',
    description="docker-rpm-builder",
    author="Alan Franzoni",
    author_email="username@franzoni.eu",
    url="https://github.com/alanfranz/docker-rpm-builder",
    version='2.0.dev',
    packages=find_packages(),
    install_requires=[
        'Click==3.3',
        'setuptools'
    ],
    entry_points='''
        [console_scripts]
        drb=drb.cmdline:cmdline
    ''',
    include_package_data=True,
    zip_safe=False

)

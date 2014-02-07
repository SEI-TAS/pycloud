__author__ = 'jdroot'

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='pycloud',
    version='0.1',
    description='Cloudlet server implementation',
    author='James Root - Software Engineering Institute',
    author_email='jdroot@sei.cmu.edu',
    url='',
    install_requires=[
        "Pylons>=0.9.7",
        "Routes==1.11",
        "mako>=0.5",
        ],
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [paste.app_factory]
    main = pycloud:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    )

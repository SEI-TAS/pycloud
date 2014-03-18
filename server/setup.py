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
    description='Cloudlet Server',
    author='Software Engineering Institute',
    author_email='',
    url='',
    install_requires=[
        "Pylons==0.9.7",
        "Routes==1.11",
        "webob==1.0.8",
        "WebTest==1.4.3",        
        "mako>=0.5",
        "pymongo>=2.6.3",
        "paramiko"
        ],
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [paste.app_factory]
    api = pycloud.api:make_app
    manager = pycloud.manager:make_app

    [paste.app_install]
    api = pylons.util:PylonsInstaller
    manager = pylons.util:PylonsInstaller
    """,
    )

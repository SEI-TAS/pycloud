__author__ = 'jdroot'

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='cloudlet-manager',
    version='0.1',
    description='Cloudlet server API implementation',
    author='Software Engineering Institute',
    author_email='',
    url='',
    install_requires=[
        "Pylons==0.9.7",
        "Routes==1.11",
        "webob==1.0.8",
        "WebTest==1.4.3",        
        "mako>=0.5",
        "pymongo>=2.6.3"
        ],
#    install_requires=[
#        "webob>=1.3.1",
#        "Pylons>=1.0.1",
#        "Routes>=1.12",
#        "mako>=0.5",
#        "pymongo>=2.6.3"
#        ],        
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [paste.app_factory]
    main = pycloud.manager:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    )

__author__ = 'jdroot'

from setuptools import setup, find_packages
from pip.req import parse_requirements

#Parse the requirements file
reqs = [str(ir.req) for ir in parse_requirements('requirements.txt')]

setup(
    name='pycloud',
    version='0.1',
    description='Cloudlet Server',
    author='Software Engineering Institute',
    author_email='James Root <jdroot@sei.cmu.edu>',
    url='',
    install_requires=reqs,
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [console_scripts]
    pycloud=pycloud:main

    [paste.app_factory]
    api = pycloud.api:make_app
    manager = pycloud.manager:make_app

    [paste.app_install]
    api = pylons.util:PylonsInstaller
    manager = pylons.util:PylonsInstaller
    """
)

__author__ = 'jdroot'


def create_cloudlet(config={}):
    from pycloud import create_cloudlet as _create_cloudlet
    return _create_cloudlet(config)
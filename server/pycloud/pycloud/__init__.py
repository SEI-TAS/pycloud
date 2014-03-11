__author__ = 'jdroot'

from cloudlet import Cloudlet as _Cloudlet

Cloudlet = _Cloudlet


def create_cloudlet(config):

    return Cloudlet(config)
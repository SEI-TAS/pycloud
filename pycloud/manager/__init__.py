__author__ = 'jdroot'

def make_app(*args, **kwargs):
    from pycloud.manager.config.middleware import make_app as _make_app
    return _make_app(*args, **kwargs)
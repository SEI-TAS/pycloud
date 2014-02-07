__author__ = 'jdroot'

def make_app(*args, **kwargs):
    from config.middleware import make_app as _make_app
    return _make_app(*args, **kwargs)
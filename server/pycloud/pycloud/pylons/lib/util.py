__author__ = 'jdroot'

from bson.json_util import dumps
from pymongo.cursor import Cursor

def asjson(f):
    def _asjson(*args):
        ret = f(*args)

        if isinstance(ret, Cursor):
            obj = []
            for item in ret:
                obj.append(obj_to_dict(item))
            ret = dict_to_json({ret.collection.name: obj})
        else:
            ret = dict_to_json(obj_to_dict(ret))
        return ret
    return _asjson

def obj_to_dict(obj):
    ret = obj
    if hasattr(ret, 'external'):
        if hasattr(ret.external, '__call__'):
            ret = ret.external()
    return ret

def dict_to_json(obj):
    ret = obj
    if isinstance(ret, Cursor) or isinstance(ret, dict):
        ret = dumps(ret)
    return ret

def dump(obj):
    for attr in dir(obj):
        print "obj.%s = %s" % (attr, getattr(obj, attr))
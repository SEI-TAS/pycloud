__author__ = 'jdroot'

from bson.json_util import dumps
from pymongo.cursor import Cursor

def asjson(f):
    def _asjson(*args):
        ret = f(*args)
        if isinstance(ret, Cursor) or isinstance(ret, dict):
            ret = dumps(ret)
        return ret
    return _asjson
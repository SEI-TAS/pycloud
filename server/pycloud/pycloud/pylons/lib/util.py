__author__ = 'jdroot'

json_lib = True
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json_lib = False
from bson.py3compat import PY3, binary_type, string_types
import bson
from bson import RE_TYPE
from bson.binary import Binary
from bson.code import Code
from bson.dbref import DBRef
from bson.max_key import MaxKey
from bson.min_key import MinKey
from bson.objectid import ObjectId
from bson.timestamp import Timestamp
import base64
import calendar
import datetime
import re
from pymongo.cursor import Cursor


def asjson(f):
    def _handle_cursor(ret):
        if isinstance(ret, Cursor):
            obj = []
            for item in ret:
                obj.append(obj_to_dict(item))
            return obj

    def _handler(ret):
        if isinstance(ret, Cursor):
            obj = _handle_cursor(ret)
            ret = dict_to_json({ret.collection.name: obj})
        else:
            ret = dict_to_json(obj_to_dict(ret))
        return ret
    if hasattr(f, '__call__'):
        def _asjson(*args):
            ret = f(*args)
            return _handler(ret)
        return _asjson
    else:
        if isinstance(f, Cursor):
            return _handle_cursor(f)
        else:
            return _handler(f)


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


def dumps(obj, *args, **kwargs):
    """Helper function that wraps :class:`json.dumps`.

    Recursive function that handles all BSON types including
    :class:`~bson.binary.Binary` and :class:`~bson.code.Code`.
    """
    if not json_lib:
        raise Exception("No json library available")
    return json.dumps(_json_convert(obj), *args, **kwargs)


def _json_convert(obj):
    """Recursive helper method that converts BSON types so they can be
    converted into json.
    """
    # Filters on external
    obj = obj_to_dict(obj)
    if hasattr(obj, 'iteritems') or hasattr(obj, 'items'):  # PY3 support
        return dict(((k, _json_convert(v)) for k, v in obj.iteritems()))
    try:
        return default(obj)
    except TypeError:
        return obj


def default(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Modified to return str(obj) instead of {$oid: str(obj)}
    if isinstance(obj, Cursor):  # If we have a cursor, convert every item
        return list(_json_convert(v) for v in obj)
    if isinstance(obj, DBRef):
        return _json_convert(obj.as_doc())
    if isinstance(obj, datetime.datetime):
        # TODO share this code w/ bson.py?
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(calendar.timegm(obj.timetuple()) * 1000 +
                     obj.microsecond / 1000)
        return {"$date": millis}
    if isinstance(obj, RE_TYPE):
        flags = ""
        if obj.flags & re.IGNORECASE:
            flags += "i"
        if obj.flags & re.LOCALE:
            flags += "l"
        if obj.flags & re.MULTILINE:
            flags += "m"
        if obj.flags & re.DOTALL:
            flags += "s"
        if obj.flags & re.UNICODE:
            flags += "u"
        if obj.flags & re.VERBOSE:
            flags += "x"
        return {"$regex": obj.pattern,
                "$options": flags}
    if isinstance(obj, MinKey):
        return {"$minKey": 1}
    if isinstance(obj, MaxKey):
        return {"$maxKey": 1}
    if isinstance(obj, Timestamp):
        return {"t": obj.time, "i": obj.inc}
    if isinstance(obj, Code):
        return {'$code': "%s" % obj, '$scope': obj.scope}
    if isinstance(obj, Binary):
        return {'$binary': base64.b64encode(obj).decode(),
                '$type': "%02x" % obj.subtype}
    if PY3 and isinstance(obj, binary_type):
        return {'$binary': base64.b64encode(obj).decode(),
                '$type': "00"}
    if bson.has_uuid() and isinstance(obj, bson.uuid.UUID):
        return {"$uuid": obj.hex}
    raise TypeError("%r is not JSON serializable" % obj)
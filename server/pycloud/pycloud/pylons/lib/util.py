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

import urllib

#############################################################################################################
# Decodes a URL encoded body with json data, parsing it and putting it into a dict.
#############################################################################################################
def encoded_json_to_dict(url_encoded_data):
    parsed_json_string = urllib.unquote(url_encoded_data)
    if parsed_json_string.endswith("="):
        parsed_json_string = parsed_json_string[:-1]
    fields = json.loads(parsed_json_string)
    return fields

def asjson2(func):
    def _func(*args, **kwargs):
        return func(*args, **kwargs)
    return _func


def asjson(f):
    # Handler to handle the result
    def _handler(ret):
        # We need to wrap cursor in dict if it is the only item
        if isinstance(ret, Cursor):
            ret = {ret.collection.name: ret}
        return dumps(ret)

    # If f is a function, we must return a callable function
    if hasattr(f, '__call__'):
        def _asjson(*args, **kwargs):
            # Get the functions code
            co = f.func_code
            # Check if the function has a kwargs argument.
            # We cannot just check the name because it could be anything
            # which means we have to check the flags. 0x08 is set if keywords is set
            varkeywords = co.co_flags & 0x08 > 0

            # If we do not have a kwargs arg we need to strip the passed in kwargs so it matches
            if not varkeywords:
                names = co.co_varnames
                _kwargs = {}
                for name in names:
                    if name in kwargs:
                        _kwargs[name] = kwargs[name]
                kwargs = _kwargs

            return _handler(f(*args, **kwargs))
        return _asjson
    else:  # Otherwise, just handle the result
        return _handler(f)


def obj_to_dict(obj):
    ret = obj
    if hasattr(ret, 'external'):
        if hasattr(ret.external, '__call__'):
            ret = ret.external()
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
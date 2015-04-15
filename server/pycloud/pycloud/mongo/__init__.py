__author__ = 'jdroot'

from model import Model as _Model
from model import AttrDict as _DictObject
from bson.objectid import ObjectId as _ObjectID

Model = _Model
DictObject = _DictObject
ObjectID = _ObjectID


_mongo_conn = None


def set_connection(conn):
    global _mongo_conn
    _mongo_conn = conn


def get_conn():
    global _mongo_conn
    return _mongo_conn
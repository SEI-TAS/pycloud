__author__ = 'jdroot'

from collection import MongoCollection
from pylons import g


class MetaInfo(object):

    collection = None
    external = None
    mapping = None

    def __init__(self, meta):
        self.__dict__.update(meta.__dict__)


class MetaObject(type):

    def __new__(mcs, name, bases, attrs):
        new_class = super(MetaObject, mcs).__new__(mcs, name, bases, attrs)

        try:
            meta = getattr(new_class, 'Meta')
            delattr(new_class, 'Meta')
        except:
            meta = None

        # Will be none for Model
        if meta is not None:
            info = MetaInfo(meta)
            info.collection = info.collection or name.lower()

            # Create the collection and add it to the new class
            coll = MongoCollection(g.cloudlet.db, info.collection, obj_class=new_class)
            new_class._collection = coll

            #Create the external attributes list and add it to the new class
            if isinstance(info.external, list):
                new_class._external = info.external
            else:
                new_class._external = None

            if isinstance(info.mapping, dict):
                new_class.variable_mapping = info.mapping
            else:
                new_class.variable_mapping = None

            # Setup find and find one static methods
            new_class.find = new_class._collection.find
            new_class.find_one = new_class._collection.find_one
            new_class.external = external

        return new_class

def external(obj):
    ret = obj
    if hasattr(ret, '_external'):
        if isinstance(ret._external, list):
            ret = {}
            for key in obj._external:
                tmp = obj[key]
                if hasattr(tmp, 'external'):
                    if hasattr(tmp.external, '__call__'):
                        tmp = tmp.external()
                ret[key] = tmp
    return ret
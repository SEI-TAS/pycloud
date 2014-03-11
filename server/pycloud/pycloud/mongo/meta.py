__author__ = 'jdroot'

from collection import MongoCollection
from pylons import g

class MetaInfo(object):

    collection = None

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

            coll = MongoCollection(g.db, info.collection, obj_class=new_class)

            new_class._collection = coll

            # Setup find and find one static methods
            new_class.find = new_class._collection.find
            new_class.find_one = new_class._collection.find_one

        return new_class
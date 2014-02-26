__author__ = 'jdroot'

from pymongo.collection import Collection
from cursor import MongoCursor

class MongoCollection(Collection):

    def __init__(self, *args, **kwargs):

        self.obj_class = kwargs.pop('obj_class')

        super(MongoCollection, self).__init__(*args, **kwargs)

    def find(self, *args, **kwargs):
        return MongoCursor(self, *args, obj_class=self.obj_class, **kwargs)

    def find_one(self, *args, **kwargs):
        document = super(MongoCollection, self).find_one(*args, **kwargs)
        if document:
            return self.obj_class(document)
        return None
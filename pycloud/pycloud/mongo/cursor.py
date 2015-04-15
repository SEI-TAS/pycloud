__author__ = 'jdroot'

from pymongo.cursor import Cursor


class MongoCursor(Cursor):

    def __init__(self, *args, **kwargs):
        self.obj_class = kwargs.pop('obj_class')
        super(MongoCursor, self).__init__(*args, **kwargs)

    def next(self):
        document = super(MongoCursor, self).next()
        return self.obj_class(document)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return super(MongoCursor, self).__getitem__(index)
        else:
            return self.obj_class(super(MongoCursor, self).__getitem__(index))
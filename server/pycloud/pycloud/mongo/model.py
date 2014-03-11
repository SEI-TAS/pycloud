__author__ = 'jdroot'

from meta import MetaObject


class AttrDict(dict):

    def __getattr__(self, attr):
        try:
            return super(AttrDict, self).__getitem__(attr)
        except KeyError as excn:
            raise AttributeError(excn)

    def __setattr__(self, attr, value):
        try:
            self[attr] = value
        except KeyError as excn:
            raise AttributeError(excn)

    def __delattr__(self, key):
        try:
            return super(AttrDict, self).__delitem__(key)
        except KeyError as excn:
            raise AttributeError(excn)

    def __setitem__(self, key, value):
        _value = value
        if isinstance(_value, dict):
            _value = AttrDict(_value)
        return super(AttrDict, self).__setitem__(key, _value)


class Model(AttrDict):
    __metaclass__ = MetaObject

    @staticmethod
    def find_one(*args, **kwargs):
        return Model._collection.find_one(args, kwargs)

    def save(self, *args, **kwargs):
        self._collection.save(self, *args, **kwargs)
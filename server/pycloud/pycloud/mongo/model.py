__author__ = 'jdroot'

from meta import MetaObject


class AttrDict(dict):

    def __getattr__(self, attr):
        try:
            print 'getting attribute: ', attr
            print type(self)
            print self
            _value = super(AttrDict, self).__getitem__(attr)
            if type(_value) is dict:
                if attr in self.__class__.variable_mapping:
                    _value = self.__class__.variable_mapping[attr](_value)
                else:
                    _value = AttrDict(_value)
                self[attr] = _value # We overwrite the dict with the wrapper
            return _value
        except KeyError as excn:
            raise AttributeError(excn)

    def __setattr__(self, attr, value):
        print 'Setting attr %s = %s on %s' % (attr, value, type(self))
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
        print 'Setting %s = %s on %s' % (key, value, type(self))
        _value = value
        # if isinstance(_value, dict):
        #     if self.__class__.variable_mapping:
        #         if key in self.__class__.variable_mapping:
        #             _value = self.__class__.variable_mapping[key](_value)
        #         else:
        #             _value = AttrDict(_value)
        #     else:
        #         _value = AttrDict(_value)
        return super(AttrDict, self).__setitem__(key, _value)


class Model(AttrDict):
    __metaclass__ = MetaObject

    @staticmethod
    def find_one(*args, **kwargs):
        return Model._collection.find_one(args, kwargs)

    def save(self, *args, **kwargs):
        self._collection.save(self, *args, **kwargs)
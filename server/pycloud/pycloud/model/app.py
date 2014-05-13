__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model, ObjectID
import os

class App(Model):
    class Meta:
        collection = "apps"
        external = ['_id', 'name', 'service_id', 'description', 'package_name',
                    'min_android_version', 'md5sum', 'app_version', 'tags']
        mapping = {

        }

    def __init__(self, *args, **kwargs):
        # self._id = None  # Commented out make Mongo auto populate it
        self.name = None
        self.service_id = None
        self.description = None
        self.package_name = None
        self.min_android_version = None
        self.md5sum = None
        self.app_version = None
        self.tags = None
        self.apk_file = None
        super(App, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate an App by its ID
    ################################################################################################################
    @staticmethod
    def by_id(oid=None):
        rid = oid
        if not isinstance(rid, ObjectID):
            # noinspection PyBroadException
            try:
                rid = ObjectID(rid)
            except:
                return None
        return App.find_one({'_id': rid})

    def file_name(self):
        return os.path.basename(self.apk_file)
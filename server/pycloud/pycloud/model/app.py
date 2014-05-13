__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model

class App(Model):
    class Meta:
        collection = "apps"
        external = ['_id', 'name', 'service_id', 'description', 'package_name',
                    'min_android_version', 'md5sum', 'app_version', 'tags']
        mapping = {

        }

    def __init__(self, *args, **kwargs):
        self._id = None
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
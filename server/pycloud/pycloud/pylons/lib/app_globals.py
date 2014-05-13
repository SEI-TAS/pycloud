"""The application's Globals object"""

from pylons import config

from pycloud.pycloud.cloudlet import get_cloudlet_instance

class Globals(object):

    # Globals acts as a container for objects available throughout the
    # life of the application.

    def __init__(self):
        # One instance of Globals is created during application
        # initialization and is available during requests via the
        # 'g' variable.

        # Create or get instance of the singleton Cloudlet object.
        self.cloudlet = get_cloudlet_instance(config)
 
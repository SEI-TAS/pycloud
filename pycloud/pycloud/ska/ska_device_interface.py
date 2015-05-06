__author__ = 'Sebastian'

######################################################################################################################
# Interface for a device that can be used for a Secure Key Authorization exchange.
######################################################################################################################
class ISKADevice:

    def connect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def get_id(self):
        raise NotImplementedError()

    def send_files(self, file_list):
        raise NotImplementedError()
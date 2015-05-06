__author__ = 'Sebastian'

"""
A simple Python script to send messages to a sever over Bluetooth
using PyBluez (with Python 2).
"""

import bluetooth
import sys
import subprocess

#import pycloud.pycloud.ska.ska_device_interface.ISKADevice
from ska_device_interface import ISKADevice

######################################################################################################################
#
######################################################################################################################
def get_adapter_address():
    internal_address = None
    cmd = subprocess.Popen('hciconfig', shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if "BD Address" in line:
            internal_address = line.split(' ')[2]

    if internal_address is not None:
        print "Bluetooth adapter with address {} found".format(internal_address)
    else:
        print "Bluetooth adapter not found."

    return internal_address

######################################################################################################################
#
######################################################################################################################
def find_bluetooth_devices():
    print('Finding bluetooth devices')
    devices = bluetooth.discover_devices(duration=3, lookup_names=True)
    print 'Devices found: ' + str(devices)
    return devices

######################################################################################################################
#
######################################################################################################################
def find_ska_service(device_address=None):
    print('Searching for the SKA secure service')
    uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
    service_matches = bluetooth.find_service(uuid=uuid, address=device_address)
    print 'Services found: ' + str(service_matches)

    if len(service_matches) == 0:
        print("couldn't find the SKA service =(")

    return service_matches

######################################################################################################################
#
######################################################################################################################
def connect_to_device(device_info):
    port = device_info["port"]
    name = device_info["name"]
    host = device_info["host"]

    print("Connecting to \"%s\" on %s" % (name, host))

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.connect((host, port))

    return socket

######################################################################################################################
#
######################################################################################################################
def comm_test(device_socket):
    print('type: ')
    while 1:
        text = raw_input()
        if text == "quit":
            break
        if text == "get_id":
            print('Getting id...')
        device_socket.send(text)

        # Wait for reply.
        reply = device_socket.recv(4096)
        print 'Reply: ' + str(reply)

######################################################################################################################
#
######################################################################################################################
class BluetoothSKAAdapter(ISKADevice):

    device_socket = None

    ####################################################################################################################
    #
    ####################################################################################################################
    def list_devices(self):
        # Check that there is a Bluetooth adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            return Exception("Bluetooth adapter not available.")

        # Find a device that has the service we want to use.
        devices = find_ska_service()

        return devices

    ####################################################################################################################
    #
    ####################################################################################################################
    def connect(self, device):
        # Check that there is a Bluetooth adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            raise Exception("Bluetooth adapter not available.")

        # Connect to the device.
        self.device_socket = connect_to_device(device)
        if self.device_socket is None:
            return False
        else:
            return True

    ####################################################################################################################
    #
    ####################################################################################################################
    def disconnect(self):
        if self.device_socket is not None:
            self.device_socket.close()

    ####################################################################################################################
    #
    ####################################################################################################################
    def get_id(self):
        if self.device_socket is None:
            raise Exception("Not connected to a device.")

        self.device_socket.send('id')

        # Wait for reply.
        device_id = self.device_socket.recv(4096)
        print 'Reply: ' + str(device_id)

        return device_id

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_files(self, file_list):
        raise NotImplementedError()

######################################################################################################################
# "Main"
######################################################################################################################

adapter = BluetoothSKAAdapter()
devices = adapter.list_devices()

if len(devices) < 0:
    sys.exit(0)

adapter.connect(devices[0])
adapter.get_id()
adapter.disconnect()

# KVM-based Discoverable Cloudlet (KD-Cloudlet)
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
#
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
#
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
#
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license
import json
import os
import subprocess

import ska_constants

try:
    from pycloud.pycloud.security import encryption
except:
    from ..security import encryption

# Size of a chunk when transmitting through TCP .
CHUNK_SIZE = 4096


########################################################################################################################
#
########################################################################################################################
class WiFiAdapter(object):
    ####################################################################################################################
    # Checks that there is an enabled WiFi device, and returns its name.
    ####################################################################################################################
    def get_adapter_name(self):
        internal_name = None

        cmd = subprocess.Popen('iw dev', shell=True, stdout=subprocess.PIPE)
        for line in cmd.stdout:
            if "Interface" in line:
                internal_name = line.split(' ')[1]
                internal_name = internal_name.replace("\n", "")
                break

        if internal_name is not None:
            print "WiFi adapter with name {} found".format(internal_name)
        else:
            print "WiFi adapter not found."

        return internal_name


########################################################################################################################
#
########################################################################################################################
class WiFiSKACommunicator(object):
    ####################################################################################################################
    #
    ####################################################################################################################
    def __init__(self, data_socket, encryption_secret, local_fqdn):
        self.data_socket = data_socket
        self.encryption_secret = encryption_secret
        self.local_fqdn = local_fqdn

    ####################################################################################################################
    # Sends a command.
    ####################################################################################################################
    def send_command(self, command, data):
        # Prepare command.
        message = dict(data)
        message['wifi_command'] = command
        message['cloudlet_name'] = self.local_fqdn
        message_string = json.dumps(message)

        # Send command.
        self._send_string(message_string)

        # Wait for reply, it should be small enough to fit in one chunk.
        reply = self._receive_string()
        return reply

    ####################################################################################################################
    #
    ####################################################################################################################
    def receive_command(self):
        received_data = self._receive_string()
        message = json.loads(received_data)

        if 'wifi_command' not in message:
            raise Exception('Invalid message received: it does not contain a wifi_command field.')
        command = message['wifi_command']

        return command, message

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_data(self, data_pair):
        data_key = data_pair[0]
        data_value = data_pair[1]
        self._send_string(
            json.dumps({ska_constants.RESULT_KEY: ska_constants.SUCCESS, data_key: data_value}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_success_reply(self):
        self._send_string(json.dumps({ska_constants.RESULT_KEY: ska_constants.SUCCESS}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_error_reply(self, error):
        self._send_string(
            json.dumps({ska_constants.RESULT_KEY: ska_constants.ERROR, ska_constants.ERROR_MSG_KEY: error}))

    ####################################################################################################################
    # Checks the success of a result.
    ####################################################################################################################
    def parse_result(self, result):
        # Check error and log it.
        json_data = json.loads(result)
        if json_data[ska_constants.RESULT_KEY] != ska_constants.SUCCESS:
            error_message = 'Error processing command on device: ' + json_data[ska_constants.ERROR_MSG_KEY]
            raise Exception(error_message)

        return json.loads(result)

    ####################################################################################################################
    # Sends a short string.
    ####################################################################################################################
    def _send_string(self, data_string):
        print 'Sending data: ' + data_string
        encrypted_data = encryption.encrypt_message(data_string, self.encryption_secret)
        self.data_socket.send(encrypted_data)

    ####################################################################################################################
    #
    ####################################################################################################################
    def _receive_string(self):
        data = self.data_socket.recv(CHUNK_SIZE)
        decrypted_data = encryption.decrypt_message(data, self.encryption_secret)
        print 'Received data: ' + decrypted_data
        return decrypted_data

    ####################################################################################################################
    # Sends a given file, ensuring the other side is ready to store it.
    ####################################################################################################################
    def send_file(self, file_path):
        print 'Sending file.'
        with open(file_path, 'rb') as file_to_send:
            file_data = file_to_send.read()

        encrypted_file_data = encryption.encrypt_message(file_data, self.encryption_secret)

        # First send the file size in bytes.
        file_size = len(encrypted_file_data)
        self._send_string(str(file_size))
        reply = self._receive_string()
        if reply == 'ack':
            self._send_file_contents(encrypted_file_data)

            # Wait for final result.
            print 'Finished sending file. Waiting for result.'
            reply = self._receive_string()
            return reply

    ####################################################################################################################
    #
    ####################################################################################################################
    def receive_file(self, message, base_path):
        file_path = os.path.join(base_path, message['file_id'])
        self._send_string('ack')

        size = int(self._receive_string())
        self._send_string('ack')
        if size > 0:
            encrypted_data = self._receive_file_contents(size)

            file_data = encryption.decrypt_message(encrypted_data, self.encryption_secret)
            with open(file_path, 'wb') as file_to_receive:
                file_to_receive.write(file_data)

            print 'File received.'

    ####################################################################################################################
    #
    ####################################################################################################################
    def _send_file_contents(self, file_data):
        # Send until there is no more data in the file.
        chunks = [file_data[i:i + CHUNK_SIZE] for i in range(0, len(file_data), CHUNK_SIZE)]
        for data_chunk in chunks:
            sent = self.data_socket.send(data_chunk)
            if sent < len(data_chunk):
                print 'Error sending data chunk.'

        print 'File sent.'

    ####################################################################################################################
    #
    ####################################################################################################################
    def _receive_file_contents(self, size):
        # Get until there is no more data in the socket.
        print 'Receiving file.'
        file_data = ''
        while True:
            received = self.data_socket.recv(CHUNK_SIZE)
            if not received:
                break
            else:
                file_data += str(received)

            if len(file_data) == size:
                break

        return file_data


########################################################################################################################
#
########################################################################################################################
class TestAdapter(object):
    def __init__(self, name):
        self.name = name

    def get_adapter_name(self):
        return self.name

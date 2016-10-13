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

from pycloud.pycloud.security import encryption

# Size of a chunk when transmitting through TCP .
CHUNK_SIZE = 4096


########################################################################################################################
#
########################################################################################################################
class WiFiSKACommunicator(object):
    ####################################################################################################################
    #
    ####################################################################################################################
    def __init__(self, data_socket, encryption_secret):
        self.data_socket = data_socket
        self.encryption_secret = encryption_secret

    ####################################################################################################################
    # Sends a short string.
    ####################################################################################################################
    def send_string(self, data_string):
        print 'Sending data: ' + data_string
        encrypted_data = encryption.encrypt_message(data_string, self.encryption_secret)
        self.data_socket.send(encrypted_data)

    ####################################################################################################################
    #
    ####################################################################################################################
    def receive_string(self):
        data = self.data_socket.recv(CHUNK_SIZE)
        decrypted_data = encryption.decrypt_message(data, self.encryption_secret)
        print 'Received data: ' + decrypted_data
        return decrypted_data

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_file(self, file_path):
        # Open, encrypt and send the file in chunks.
        print 'Sending file.'
        with open(file_path, 'rb') as file_to_send:
            file_data = file_to_send.readall()

        encrypted_file_data = encryption.encrypt_message(file_data, self.encryption_secret)

        # Send until there is no more data in the file.
        while True:
            data_chunk = encrypted_file_data.read(CHUNK_SIZE)
            if not data_chunk:
                print 'File sent.'
                break

            sent = self.data_socket.send(data_chunk)
            if sent < len(data_chunk):
                print 'Error sending data chunk.'

    ####################################################################################################################
    #
    ####################################################################################################################
    def receive_file(self, file_path):
        # Get until there is no more data in the socket.
        print 'Receiving file.'
        encrypted_data = ''
        while True:
            received = self.data_socket.recv(CHUNK_SIZE)
            if not received:
                break
            else:
                encrypted_data += str(received)

        file_data = encryption.decrypt_message(encrypted_data, self.encryption_secret)
        with open(file_path, 'wb') as file_to_receive:
            file_to_receive.write(file_data)

        print 'File received.'

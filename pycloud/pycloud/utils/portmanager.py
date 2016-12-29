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

#!/usr/bin/env python
#       

import random
import socket


################################################################################################################
# Handles TCP ports.
################################################################################################################
class PortManager(object):

    ################################################################################################################
    # Generate a random port number which is available.
    ################################################################################################################ 
    @staticmethod  
    def generate_random_available_port():
        # The range of ports were we will take a port from.
        range_start = 10000
        range_end = 60000
        
        # In practice, this loop will almost always run once, since we will not be handling that many
        # running instances to generate collisions.
        max_attempts = 5000
        num_attempts = 0
        while True:
            # Get a new random port.
            num_attempts += 1
            port = random.randint(range_start, range_end)

            # Check if the port is in use.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            port_is_in_use = result == 0
            if not port_is_in_use:
                # If the port is available, stop looking for more ports.
                return port

            if num_attempts >= max_attempts:
                raise Exception("Too many ports tried, no ports available found.")

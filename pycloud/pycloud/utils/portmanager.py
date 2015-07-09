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

# To generate random port numbers.
import random

################################################################################################################
# Handles TCP ports.
# TODO: this list has to be stored in the DB.
################################################################################################################
class PortManager(object):
    
    # Stores a list of ports in use.
    portsInUse = {}
    
    ################################################################################################################  
    # Generate a random port number which is available (in terms of this manager not using it). There is no check to
    # see if another process is using the port.
    ################################################################################################################ 
    @staticmethod  
    def generateRandomAvailablePort():
        # The range of ports were we will take a port from.
        rangeStart = 10000
        rangeEnd = 60000
        
        # Check if we still have ports available.
        if(len(PortManager.portsInUse) >= (rangeEnd - rangeStart)):
            raise Exception("There are no ports available.")
        
        # This loop will eventually find an available port, since if all of them are in use, the check above would
        # have detected it. In practice, this loop will almost always run once, since we will not be handling that many
        # running instances to generate collisions.
        port = 0
        while(True):
            # Get a new random port and check if it is in use.
            port = random.randint(rangeStart, rangeEnd)
            if(not port in PortManager.portsInUse):
                # If the port is available, stop looking for more ports.
                PortManager.portsInUse[port] = True
                break

        return port
    
    ################################################################################################################  
    # Marks a given port as cleared.
    ################################################################################################################ 
    @staticmethod  
    def freePort(port):
        PortManager.portsInUse.pop(port, None)

    ################################################################################################################  
    # Marks all ports as free.
    ################################################################################################################ 
    @staticmethod  
    def clearPorts():
        PortManager.portsInUse.clear()
        
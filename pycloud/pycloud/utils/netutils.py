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
import time

import netifaces
import netaddr

from subprocess import Popen, PIPE
from xml.etree import ElementTree

################################################################################################################
# Various net-related utility functions.
################################################################################################################

################################################################################################################
# Generates a random MAC address.
################################################################################################################
def generate_random_mac():
    mac = [
        0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

################################################################################################################
# Returns the IP of the given adapter.
################################################################################################################
def get_adapter_ip_address(adapter_name, ip_position=0):
    addr_info = netifaces.ifaddresses(adapter_name)[netifaces.AF_INET][ip_position]
    return addr_info['addr']

################################################################################################################
# Will locate the IP address for a given mac address
################################################################################################################
def find_ip_for_mac(mac, adapter, nmap='nmap', retry=5):
    if retry == 0:
        print 'No more retries, IP not found.'
        return None

    # Get the ip range of the given adapter.
    addr_info = netifaces.ifaddresses(adapter)[netifaces.AF_INET][0]
    ip_range = str(netaddr.IPNetwork('%s/%s' % (addr_info['addr'], addr_info['netmask'])))

    print 'Scanning range %s for MAC address %s' % (ip_range, mac)
    p = Popen(['sudo', nmap, '-sP', ip_range, '-oX', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    if rc != 0:
        print "Error executing nmap:\n%s" % err
        raise Exception("Error executing nmap:\n%s" % err)
    xml = ElementTree.fromstring(out)
    try:
        ip = xml.find('./host/address[@addr="%s"]/../address[@addrtype="ipv4"]' % mac.upper()).get('addr')
        print 'Found IP: ', ip
    except:
        print 'Failed to find IP, retrying...'
        time.sleep(1)
        ip = find_ip_for_mac(mac, adapter, nmap, retry=(retry - 1))

    return ip

################################################################################################################
# Checks if a given port is open on a given IP address.
################################################################################################################
def is_port_open(ip_address, port):
    print 'Checking if port ' + str(port) + ' is open on IP ' + str(ip_address)
    timeout = 0.2
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((ip_address, port))
    return result == 0

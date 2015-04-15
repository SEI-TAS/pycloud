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

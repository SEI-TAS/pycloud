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

import dns.update
import dns.query
import dns.tsigkeyring

#######################################################################################################################
# Sends a dynamic update to a local DNS server.
#######################################################################################################################
def _send_dynamic_update(command):
    # Send the update command to the local DNS server.
    response = dns.query.tcp(command, '127.0.0.1', timeout=10)
    print response

#######################################################################################################################
# Adds a DNS record dynamically.
# - zone: the name of the zone
# - key: the value of th TSIG key
# - host: the record name, usually a host name
# - value: the value to set that record to, usually an IP, hostname or FQDN.
#######################################################################################################################
def add_dns_record(zone, key, host, value, record_type='CNAME'):
    # Shared secret.
    key_name = zone
    keyring = dns.tsigkeyring.from_text({key_name: key})

    # Prepare the update command.
    update_command = dns.update.Update(zone, keyring=keyring)
    update_command.add(host, 300, record_type, value)

    # Send the update command to the local DNS server.
    _send_dynamic_update(update_command)

#######################################################################################################################
# Removes a DNS record dynamically.
# - zone: the name of the zone
# - key: the value of th TSIG key
# - host: the record name, usually a host name
#######################################################################################################################
def remove_dns_record(zone, key, host):
    # Shared secret.
    key_name = zone
    keyring = dns.tsigkeyring.from_text({key_name: key})

    # Prepare the update command.
    update_command = dns.update.Update(zone, keyring=keyring)
    update_command.delete(host)

    # Send the update command to the local DNS server.
    _send_dynamic_update(update_command)

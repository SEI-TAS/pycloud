#!/usr/bin/env python

import dns.update
import dns.query
import dns.tsigkeyring

# Shared secret.
keyring = dns.tsigkeyring.from_text({'svm.cloudlet.local.': 'BR2bSEH3E6bIm8V5KJFT1Q=='})

# Prepare the update command.
update_command = dns.update.Update('svm.cloudlet.local.', keyring=keyring)
update_command.add('speech', 300, 'CNAME', 'cloudlet')

# Send the update command to the local DNS server.
response = dns.query.tcp(update_command, '127.0.0.1', timeout=10)
print response

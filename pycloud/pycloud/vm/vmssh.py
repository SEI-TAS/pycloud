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

# For SSH connections.
import paramiko
       
################################################################################################################
# SSH client to a runniv VM.
################################################################################################################
class VmSshClient(object):

    # The host will be localhost since we are assuming the VMs are using port forwarding.
    HOST = "localhost"
    
    # Default user and password.
    DEFAULT_USER = "cloudlet"    
    DEFAULT_PASSWORD = "cloudlet"
    
    # Max size of the return value for commands.
    MAX_RETURN_VALUE = 4096
    
    # The SSH connection.
    sshConn = None

    ################################################################################################################
    # Connects to a VM through SSH.
    ################################################################################################################           
    def __init__(self, sshPort):
        # Connect with authentication.        
        self.sshConn = paramiko.SSHClient()
        self.sshConn.load_system_host_keys()
        self.sshConn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshConn.connect(hostname = self.HOST, port = sshPort, username = self.DEFAULT_USER, password = self.DEFAULT_PASSWORD)
                
    ################################################################################################################
    # Uploads a file through SFTP to a running VM.
    # NOTE: destFilePath has to be a full file path, not only a folder.
    ################################################################################################################       
    def uploadFile(self, sourceFilePath, destFilePath):
        # Establish an SFTP session.        
        sftp = self.sshConn.open_sftp()
        
        # Upload the file.
        print 'Transfering file...'
        sftp.put(sourceFilePath, destFilePath)
        print 'File transfered.'
       
    ################################################################################################################
    # Executes a command on a VM through SSH.
    ################################################################################################################              
    def executeCommand(self, command):
        # Send the command and get the result.
        #sshStdin, sshStdout, sshStderr = self.sshConn.exec_command(command)  # @UnusedVariable
        channel = self.sshConn.invoke_shell()
        sshStdin = channel.makefile('wb')
        sshStdout = channel.makefile('rb')
        
        sshStdin.write('''
        ''' + command + '''
        exit
        ''')
            
        # Return whatever the command returned.            
        returnValue = sshStdout.read()
        
        sshStdin.close()
        sshStdout.close()
        
        return returnValue       

    ################################################################################################################
    # Ends the SSH session.
    ################################################################################################################              
    def disconnect(self):
        self.sshConn.close()
        self.sshConn = None
        
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

import os

# Used to check file existence and handle paths.
import os.path

# Used to copy files.
import shutil

# Used to change file permissions
import stat

from subprocess import Popen, PIPE

################################################################################################################
# Various file-related utility functions.
################################################################################################################

################################################################################################################
# Removes a folder and its contents (if they exist), and then creates the folder.
################################################################################################################
def recreate_folder(folder_path):
    # First remove it, if it exists.
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # Now create it.
    os.makedirs(folder_path)
        
################################################################################################################
# Creates a folder path only if it does not exist.
################################################################################################################
def create_folder_if_new(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

################################################################################################################
# Protects a VM Image by making it read-only for all users.
################################################################################################################
def make_read_only_all(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.chmod(file_path,
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

################################################################################################################
# Makes the files of a VM Image available (read and write) to all users.
################################################################################################################
def make_read_write_all(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.chmod(file_path,
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

################################################################################################################
# Changes ownership of the given file to the user running the script.
################################################################################################################
def chown_to_current_user(file_path):
    curr_user = os.geteuid()
    curr_group = os.getegid()

    # Execute sudo process to change ownershio of potentially root owned file to the current user.
    p = Popen(['sudo', 'chown', str(curr_user) + ":" + str(curr_group), file_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    if rc != 0:
        print "Error getting ownership of file:\n%s" % err
        raise Exception("Error getting ownersip of file:\n%s" % err)

##############################################################################################################
# Replaces a given string with a new one in the given file.
##############################################################################################################
def replace_in_file(original_text, new_text, filen_path):
    reg_exp = "s/ " + original_text + ";/ " + new_text + ";/g"
    command = ['/bin/sed', '-i', reg_exp, filen_path]
    Popen(command)

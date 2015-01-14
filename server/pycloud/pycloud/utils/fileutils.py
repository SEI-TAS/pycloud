#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# Used to copy files.
import shutil

# Used to change file permissions
import stat

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

#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# Used to copy files.
import shutil

################################################################################################################
# Various file-related utility functions.
################################################################################################################
class FileUtils(object):
        
    ################################################################################################################
    # Removes a folder and its contents (if they exist), and then creates the folder.
    ################################################################################################################
    @staticmethod
    def recreateFolder(folderPath):
        # First remove it, if it exists.
        if(os.path.exists(folderPath)):
            shutil.rmtree(folderPath)
            
        # Now create it.
        os.makedirs(folderPath)
        
    ################################################################################################################
    # Creates a folder path only if it does not exist.
    ################################################################################################################
    @staticmethod
    def createFolderIfNew(folderPath):
        if(not os.path.exists(folderPath)):
            os.makedirs(folderPath)        
        


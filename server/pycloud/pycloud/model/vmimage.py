__author__ = 'jdroot'

# Used to copy files.
import shutil

# Used to check file existence.
import os

# Used to change file permissions
import stat

# For disk image management.
from pycloud.pycloud.vm import diskimage
from pycloud.pycloud.vm import qcowdiskimage
from pycloud.pycloud.vm.vmsavedstate import VMSavedState

from pycloud.pycloud.mongo import DictObject

################################################################################################################
# Exception type used in this module.
################################################################################################################
class DiskImageException(Exception):
    def __init__(self, message):
        super(DiskImageException, self).__init__(message)
        self.message = message

################################################################################################################
# Represents a VM Image composed of a disk and a saved state image files.
################################################################################################################
class VMImage(DictObject):

    # Create our default attributes but then pass everything up to the super
    def __init__(self, *args, **kwargs):
        self.disk_image = None
        self.state_image = None
        self.cloned = False
        super(VMImage, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Copies an image file to a given folder.
    ################################################################################################################
    @staticmethod
    def _clone_file_to_folder(destination_folder, original):
        # Check if the source disk image file exists.
        if not os.path.exists(original):
            raise DiskImageException("Source image file does not exist (%s)." % original)

        new_file = os.path.join(destination_folder, os.path.basename(original))

        # Simply copy the file.
        print "Copying image %s to new disk image %s..." % (os.path.basename(original), destination_folder)
        shutil.copyfile(original, new_file)
        print 'Image copied.'

        return new_file

    ################################################################################################################
    # Will clone the disk and state image files to the specified folder
    ################################################################################################################
    def clone(self, destination_folder):
        # Check if the destination folder already exists
        if os.path.exists(destination_folder):
            # This is an error, as we don't want to overwrite an existing disk image with a source.
            raise DiskImageException("Destination image file already exists (%s)."
                                     "Will not overwrite existing image." % destination_folder)

        # Make the folder.
        os.makedirs(destination_folder)
        try:
            ret = VMImage()
            ret.cloned = True
            ret.disk_image = VMImage._clone_file_to_folder(destination_folder, self.disk_image)
            ret.state_image = VMImage._clone_file_to_folder(destination_folder, self.state_image)
            return ret
        except:
            # Clean up the directory we just created
            os.rmdir(destination_folder)
            raise

    ################################################################################################################
    # Creates a VM Image from a source file.
    ################################################################################################################ 
    def create(self, sourceDiskImageFilePath, destDiskImageFilePath):               
        # Create a new disk image from the source image.
        print "VM disk image creation step."
        sourceDiskImage = diskimage.DiskImage(sourceDiskImageFilePath)
        self.disk_image = destDiskImageFilePath
        newDiskImage = qcowdiskimage.Qcow2DiskImage(self.disk_image)
        newDiskImage.createFromOtherType(sourceDiskImage)
        
        # Set a default value for the saved state image file.
        self.state_image = VMSavedState.getDefaultSavedStateFile(self.disk_image)           

    ################################################################################################################
    # Protects a VM Image by making it read-only.
    ################################################################################################################
    def protect(self):                       
        # Check the disk_image
        if os.path.exists(self.disk_image) and os.path.isfile(self.disk_image):
            os.chmod(self.disk_image,
                     stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH )

        # Check the state_image
        if os.path.exists(self.state_image) and os.path.isfile(self.state_image):
            os.chmod(self.disk_image,
                     stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH )                

    ################################################################################################################
    # Makes the files of a VM Image available (read and write) to all.
    ################################################################################################################
    def unprotect(self):
        # Check the disk_image
        if os.path.exists(self.disk_image) and os.path.isfile(self.disk_image):
            os.chmod(self.disk_image,
                     stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

        # Check the state_image
        if os.path.exists(self.state_image) and os.path.isfile(self.state_image):
            os.chmod(self.disk_image,
                     stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

    ################################################################################################################
    # Cleans up the files, if this is a clone it will delete the files. Force will delete if cloned.
    ################################################################################################################
    def cleanup(self, image_folder, force=False):
        if self.cloned or force:
            if image_folder:
                if os.path.exists(image_folder):
                    if os.path.isdir(image_folder):
                        shutil.rmtree(image_folder)

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
from pycloud.pycloud.utils import fileutils

from pycloud.pycloud.mongo import DictObject

################################################################################################################
# Exception type used in this module.
################################################################################################################
class VMImageException(Exception):
    def __init__(self, message):
        super(VMImageException, self).__init__(message)
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
            raise VMImageException("Source image file does not exist (%s)." % original)

        new_file = os.path.abspath(os.path.join(destination_folder, os.path.basename(original)))

        # Simply copy the file.
        print "Copying image %s to new disk image %s..." % (os.path.basename(original), destination_folder)
        shutil.copyfile(original, new_file)
        print 'Image copied.'

        return new_file

    ################################################################################################################
    # Checks if a disk image file has a valid extension.
    ################################################################################################################
    @staticmethod
    def _is_valid_disk_image(filename):
        disk_image_extension = ".qcow2"
        return filename.endswith(disk_image_extension)

    ################################################################################################################
    # Checks if a state image file has a valid extension.
    ################################################################################################################
    @staticmethod
    def _is_valid_state_image(filename):
        state_image_extension = ".lqs"
        return filename.endswith(state_image_extension)

    ################################################################################################################
    # Loads information about a VM Image from a folder.
    ################################################################################################################
    def load_from_folder(self, folder_path):
        # Get the folder and check if it exists.
        if not os.path.exists(folder_path):
            raise VMImageException("Folder %s does not exist." % folder_path)

        # Loop over the files in the folder, finding valid image files.
        self.disk_image = None
        self.state_image = None
        file_list = os.listdir(folder_path)
        for current_filename in file_list:
            # Check if there is an image file, if so, store its path.
            if VMImage._is_valid_disk_image(current_filename):
                self.disk_image = os.path.join(folder_path, current_filename)
            elif VMImage._is_valid_state_image(current_filename):
                self.state_image = os.path.join(folder_path, current_filename)

        # If we didn't find a disk or saved state image, there is something seriously wrong.
        if self.disk_image is None:
            raise VMImageException("Folder %s did not contain a valid disk image file." % folder_path)
        if self.state_image is None:
            raise VMImageException("Folder %s did not contain a valid disk image file." % folder_path)

    ################################################################################################################
    # Will clone the disk and state image files to the specified folder
    ################################################################################################################
    def clone(self, destination_folder, clone_full_image=False):
        # Check if the destination folder already exists
        if os.path.exists(destination_folder):
            # This is an error, as we don't want to overwrite an existing disk image with a source.
            raise VMImageException("Destination image file already exists (%s)."
                                   "Will not overwrite existing image." % destination_folder)

        # Make the folder.
        os.makedirs(destination_folder)
        try:
            ret = VMImage()
            ret.cloned = True
            ret.state_image = VMImage._clone_file_to_folder(destination_folder, self.state_image)
            
            if not clone_full_image:
                # Create a shallow qcow2 file pointing at the original image, instead of copying it, for faster startup.
                # ret.disk_image = VMImage._clone_file_to_folder(destination_folder, self.disk_image)
                ret.disk_image = os.path.abspath(os.path.join(destination_folder, os.path.basename(self.disk_image)))
                clonedDiskImage = qcowdiskimage.Qcow2DiskImage(ret.disk_image)
                clonedDiskImage.linkToBackingFile(self.disk_image)
            else:
                ret.disk_image = VMImage._clone_file_to_folder(destination_folder, self.disk_image)
                
            return ret
        except:
            # Clean up the directory we just created
            os.rmdir(destination_folder)
            raise
        
    ################################################################################################################
    # Move the VM Image to the given folder.
    ################################################################################################################ 
    def move(self, destination_folder):
        try:
            # We will overwrite any existing vm image already stored with the same name.
            fileutils.recreate_folder(destination_folder)
            
            # Move the files.
            shutil.move(self.disk_image, destination_folder)
            shutil.move(self.state_image, destination_folder)
            
            # Update our paths to reflect the move.
            source_dir = os.path.dirname(self.disk_image)
            self.disk_image = os.path.abspath(os.path.join(destination_folder, os.path.basename(self.disk_image)))
            self.state_image = os.path.abspath(os.path.join(destination_folder, os.path.basename(self.state_image)))
            
            # Remove our original folder.
            os.rmdir(source_dir)
        except:
            # Clean up the directory we just created
            os.rmdir(destination_folder)
            raise

    ################################################################################################################
    # Store the disk image file in the given location, and update it internally.
    ################################################################################################################
    def store(self, destination_folder, disk_image_file_object, state_image_file_object=None):
        try:
            # Create the folder to store the files.
            fileutils.recreate_folder(destination_folder)
            new_disk_image_path = os.path.abspath(os.path.join(destination_folder, os.path.basename(self.disk_image)))
            new_state_image_path = os.path.abspath(os.path.join(destination_folder, os.path.basename(self.state_image)))

            # Transfer the disk file's data to their new location.
            new_disk_image_file = open(new_disk_image_path, 'wb')
            shutil.copyfileobj(disk_image_file_object, new_disk_image_file)
            disk_image_file_object.close()
            new_disk_image_file.close()

            # Transfer the state file's data to their new location.
            if state_image_file_object:
                new_state_image_file = open(new_state_image_path, 'wb')
                shutil.copyfileobj(state_image_file_object, new_state_image_file)
                state_image_file_object.close()
                new_state_image_file.close()

            # Update our paths to reflect the new location.
            self.disk_image = new_disk_image_path
            self.state_image = new_state_image_path
        except:
            # Clean up the directory we just created
            shutil.rmtree(destination_folder, ignore_errors=True)
            raise

    ################################################################################################################
    # Creates a VM Image from a source file. This converts the source image from whatever format into qcow2.
    ################################################################################################################ 
    def create(self, sourceDiskImageFilePath, destDiskImageFilePath):
        try:
            # Clean up the folder first.
            fileutils.recreate_folder(os.path.dirname(destDiskImageFilePath))
            
            # Create a new disk image from the source image.
            print "VM disk image creation step."
            newDiskImage = qcowdiskimage.Qcow2DiskImage(destDiskImageFilePath)
            self.disk_image = newDiskImage.filepath
            
            # Disk file will be copied or converted depending on the type.
            if(diskimage.DiskImage.getDiskImageType(sourceDiskImageFilePath) == diskimage.DiskImage.TYPE_QCOW2):
                # If it is of our target type, just copy it.
                copied_image = VMImage._clone_file_to_folder(os.path.dirname(destDiskImageFilePath), sourceDiskImageFilePath)
                os.rename(copied_image, self.disk_image)
            else:
                # Convert from original type.
                sourceDiskImage = diskimage.DiskImage(sourceDiskImageFilePath)        
                newDiskImage.createFromOtherType(sourceDiskImage)
            
            # Set a default value for the saved state image file.
            self.state_image = VMSavedState.getDefaultSavedStateFile(self.disk_image)
        except:
            # Delete the folder with the temp data.
            print 'Deleting temp folder due to error: ' + os.path.dirname(destDiskImageFilePath)
            shutil.rmtree(os.path.dirname(destDiskImageFilePath))
            raise

    ################################################################################################################
    # If appropriate, rebases this file to the given backing file.
    ################################################################################################################
    def rebase_disk_image(self, backing_disk_file):
            # Only valid for qco2 files.
            if(diskimage.DiskImage.getDiskImageType(self.disk_image) == diskimage.DiskImage.TYPE_QCOW2):
                qcow_image = qcowdiskimage.Qcow2DiskImage(self.disk_image)
                qcow_image.linkToBackingFile(backing_disk_file)
            else:
                # Nothing to do here.
                return

    ################################################################################################################
    # Protects a VM Image by making it read-only.
    ################################################################################################################
    def protect(self):                       
        fileutils.make_read_only_all(self.disk_image)
        fileutils.make_read_only_all(self.state_image)

    ################################################################################################################
    # Makes the files of a VM Image available (read and write) to all.
    ################################################################################################################
    def unprotect(self):
        fileutils.make_read_write_all(self.disk_image)
        fileutils.make_read_write_all(self.state_image)

    ################################################################################################################
    # Cleans up the files, if this is a clone it will delete the files. Force will delete even if not cloned.
    ################################################################################################################
    def cleanup(self, force=False):
        if self.cloned or force:
            image_folder = os.path.dirname(self.disk_image)
            if os.path.exists(image_folder):
                if os.path.isdir(image_folder):
                    print 'Removing VM image folder: ' + image_folder
                    shutil.rmtree(image_folder)

    ################################################################################################################
    # Returns a description of the names of the vm image files.
    ################################################################################################################
    def export(self):
        return {
            "disk_image": os.path.basename(self.disk_image),
            "state_image": os.path.basename(self.state_image)
        }
#!/usr/bin/env python
#       

# Used to check file existence.
import os.path

# The base class (from this same package).
import diskimage

# Used to start external processes.
import subprocess

################################################################################################################
# Simple structure to represent a disk image based on a qcow2 file format.
################################################################################################################
class Qcow2DiskImage(diskimage.DiskImage):
    
    ################################################################################################################
    # Sets up internal values of the disk image.
    ################################################################################################################        
    def __init__(self, diskImageFilepath):
        # Add the qcow2 extension if needed.
        imagetype = self.getDiskImageType(diskImageFilepath)
        if(imagetype == None):
            diskImageFilepath = diskImageFilepath + '.qcow2'
            
        # Call the basic constructor.
        super(Qcow2DiskImage, self).__init__(diskImageFilepath)
       
    ################################################################################################################
    # @Override.
    # Creates a disk image file referencing a source disk image file. This implies linking to a 
    # backing file if we are creating a new qcow2 file, or rebasing it if it already exists.
    ################################################################################################################           
    def linkToBackingFile(self, sourceDiskImageFilepath):
        # Check if the disk image file already exists.
        if not os.path.exists(self.filepath):
            # If it doesn't exist, we will create it based on the source image file.
            self.__createWithReference(sourceDiskImageFilepath)
        else:
            # If it does exist, we won't create it... we will just rebase it if it makes sense for this type of image.
            self.__rebase(sourceDiskImageFilepath)
        
    ################################################################################################################
    # Creates a new qcow2 image referencing the provided source image.
    ################################################################################################################  
    def __createWithReference(self, sourceDiskImageFilepath):
        # Ensure that we have the absolute path for the source image, since a relative one won't do.
        sourceDiskImageFilepath = os.path.abspath(sourceDiskImageFilepath)
                
        # We need to use the qemu-img command line tool for this.
        # Note that we set the source file as its backing file. This is stored in the qcow2 file, but it can be changed later.
        # Note that we also use 4K as the cluster size, since it seems to be the best compromise.
        print "Creating qcow2 image %s based on source image %s..." % (self.filepath, sourceDiskImageFilepath)
        imageToolCommand = 'qemu-img create -f %s -o backing_file=%s,cluster_size=4096 %s' \
                            % (self.type, sourceDiskImageFilepath, self.filepath)
        self.__runImageCreationTool(imageToolCommand)
        print 'New disk image created.'
                
    ################################################################################################################
    # Rebases a disk image file so that it points to the given base image. Only makes sense for qcow2 files.
    ################################################################################################################           
    def __rebase(self, sourceDiskImageFilepath):
        # Ensure that we have the absolute path for the source image, since a relative one won't do.
        sourceDiskImageFilepath = os.path.abspath(sourceDiskImageFilepath)
        
        # We need to use the qemu-img command line tool for this.
        print "Rebasing qcow2 image file %s with backing file %s" % (self.filepath, sourceDiskImageFilepath)
        imageToolCommand = 'qemu-img rebase -u -b %s %s' \
                            % (sourceDiskImageFilepath, self.filepath)
        self.__runImageCreationTool(imageToolCommand)
        print 'Rebasing finished.'
        
                
    ################################################################################################################
    # Creates a disk image from another type.
    ################################################################################################################           
    def createFromOtherType(self, sourceDiskImage):
        # Ensure that we have the absolute path for the source image, since a relative one won't do.
        sourceDiskImageFilepath = os.path.abspath(sourceDiskImage.filepath)
        
        # We need to use the qemu-img command line tool for this.
        print "Create qcow2 image file %s as a conversion from %s" % (self.filepath, sourceDiskImageFilepath)
        imageToolCommand = 'qemu-img convert -f %s -O qcow2 %s %s' \
                            % (sourceDiskImage.type, sourceDiskImageFilepath, self.filepath)
        self.__runImageCreationTool(imageToolCommand)
        print 'Creating from conversion finished.'              
        
    ################################################################################################################
    #  Runs the image creation tool.
    ################################################################################################################        
    def __runImageCreationTool(self, imageToolCommand):
        # Starts the image creation tool in a separate process, and waits for it.
        toolPipe = subprocess.PIPE
        toolProcess = subprocess.Popen(imageToolCommand, shell=True, stdin=toolPipe, stdout=toolPipe, stderr=toolPipe)
        normalOutput, errorOutput = toolProcess.communicate()
        
        # Show errors, if any.
        if(len(errorOutput) > 0):
            print errorOutput
            
        # Show output, if any.                
        if(len(normalOutput) > 0):
            print normalOutput

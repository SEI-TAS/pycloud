#!/usr/bin/env python
#       

# Import libvirt to access the virtualization API.
import libvirt

# Used to generate unique IDs for the VMs.
from uuid import uuid4

# Used to handle paths more easily.
import os.path

# For SSH connections (from this same package).
import vmssh

# For VNC connections (from this same package).
import vncclient

# Classes for handling disk images and vm memory states (from this same package).
import vmsavedstate
import diskimage

################################################################################################################
# Exception type used in our system.
################################################################################################################
class VirtualMachineException(Exception):
    def __init__(self, message):
        super(VirtualMachineException, self).__init__(message)
        self.message = message    

################################################################################################################
# Object that respresents a VNC-enabled Virtual Machine (transient). A new VM object can be resumed from an existing
# VM, in which case the new VM will be a clone of the original one.
# This particular implementation uses libvirt for the VM handling.
################################################################################################################
class RunningVM(object):   
    # URI used to connect to the local hypervisor.
    HYPERVISOR_URI = "qemu:///session"
    
    # Name prefix for VMs.
    VM_NAME_PREFIX = 'vm'
    
    # ID for this VM
    id = ''
    
    # Prefix for naming this VM.    
    prefix = VM_NAME_PREFIX
    
    # Default port at the host to map the SSH service.
    SSH_DEFAULT_HOST_PORT = 9022
    
    # Port where SSH server is running inside the VM.
    SSH_GUEST_PORT = 22
    
    # A client used to connect through SSH to the instance.
    sshClient = None

    # The external port in the host which will be mapped to the internal SSH server port.
    sshHostPort = None

    ################################################################################################################
    # Generates a random ID, valid as a VM id.
    ################################################################################################################        
    @staticmethod   
    def generateRandomId():
        return str(uuid4())
    
    ################################################################################################################
    # Sets up internal values of the VM.
    ################################################################################################################        
    def __init__(self, id=None, prefix=None, diskImageFile=None):
        # Set a unique id for this VM instance.
        self.id = id
        if(self.id == None):
            self.id = RunningVM.generateRandomId()
        
        # Optionally, set a prefix for VM names.
        if(prefix != None):
            self.prefix = prefix
        
        # Setup the disk image file info, if available
        if(diskImageFile != None):
            # Ensure that the disk image is an absolute path.
            diskImageFile = os.path.abspath(diskImageFile)
            
            # Store information about the disk image.
            self.diskImage = diskimage.DiskImage(diskImageFile)
        
        # Setup the port mapping info.
        self.portMappings = {}
        
        # Connect to the hypervisor.
        self.hypervisor = libvirt.open(self.HYPERVISOR_URI)
            
        # Start with an empty VM.
        self.virtualMachine = None
        
    ################################################################################################################  
    # Adds an forwarded port to the port mapping map.
    ################################################################################################################             
    def addForwardedPort(self, hostPort, guestPort):
        self.portMappings[hostPort] = guestPort
        print('Setting up port forwarding from host port ' + str(hostPort) + ' to guest port ' + str(guestPort))
        
    ################################################################################################################  
    # Adds an SSH port to the port mapping.
    ################################################################################################################             
    def addForwardedSshPort(self, sshHostPort=None):
        # Add a default port if none is given.
        if(sshHostPort == None):
            sshHostPort = self.SSH_DEFAULT_HOST_PORT
                
        # Set up the port mappings for an SSH maintenance door.
        self.addForwardedPort(sshHostPort, self.SSH_GUEST_PORT)
        self.sshHostPort = sshHostPort

    ################################################################################################################
    # Starts a VNC connection with a GUI and waits until it is closed.
    ################################################################################################################            
    def startVncAndWait(self):
        # We have to get the XML description of the running machine to find the port available for VNC.
        runningVMXmlString = self.virtualMachine.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
        runningVMElement = ElementTree.fromstring(runningVMXmlString)
        
        # We can now get the VNC port, which was automatically allocated by libvirt/qemu.
        vncPort = runningVMElement.find("devices/graphics").get("port")
        
        # Connect through the VNC client and wait.
        print 'Starting VNC GUI to VM, and waiting for user to close it.'
        vncClient = vncclient.VNCClient()
        result = vncClient.connectAndWait(vncPort)
        print 'VNC GUI no longer running, stopped waiting.'
        
        # If there was a problem, destroy the VM.
        if(result == False):
            self.destroy()
    
    ################################################################################################################
    # Starts a VM, cold booting it and ignoring any memory image.
    ################################################################################################################    
    def start(self, vmXmlTemplateFile, showVNC=False):
        # Check that the XML description file exists.
        if(not os.path.exists(vmXmlTemplateFile)):
            raise VirtualMachineException("VM description file %s for VM creation does not exist." % vmXmlTemplateFile)
         
        # Load the XML template and update it with this VM's information.
        templateXmlDescriptorString = (open(vmXmlTemplateFile, "r").read())
        self.__updateXmlDescriptorString(templateXmlDescriptorString)
        
        # Create and start a VM ("domain") through the hypervisor.
        print "Starting a new VM..."  
        try:         
            self.virtualMachine = self.hypervisor.createXML(self.xmlDescriptorString, 0)
        except:
            # Ensure we destroy the VM if there was some problem after creating it.
            self.destroy()
            raise
            
        # If a GUI was requested, start VNC and wait for the user to close the window.
        if(showVNC):
            self.startVncAndWait()
       
    ################################################################################################################
    # Resumes a VM from a memory snapshot. If showVNC is True,  it will start a VNC connection to it, and waits 
    # till the user closes the VNC window.  
    # NOTE: the saved state file will be modified to change its UUID when resuming, due to libvirt limitations.
    ################################################################################################################    
    def resume(self, savedStateFile=None, showVNC=False):
        # If no memory image was provided, we will assume its name is based on the disk image.
        if(savedStateFile == None):
            savedStateFile = self.getDefaultSavedStateFile()    
        savedState = vmsavedstate.VMSavedState(savedStateFile)        
        
        # Check if the Vm saved state file exists.
        if(not savedState.exists()):
            raise VirtualMachineException('Error resuming VM: saved state file %s does not exist.' % savedState.savedStateFilename)
        
        # Load the XML description from the saved image file, and update it with this VM's information.
        savedXmlDescriptorString = savedState.getStoredVmDescription(self.hypervisor)
        self.__updateXmlDescriptorString(savedXmlDescriptorString)
        #print updatedXmlDescriptor

        # We actually have to store the header manually in the save image file, only because libvirt won't allow us to resume
        # the VM with an different UUID from the one in the saved image.
        vmXmlDescriptor = VirtualMachineDescriptor(savedXmlDescriptorString)
        vmXmlDescriptor.setUuid(self.id)
        vmXmlDescriptor.setName(self.prefix + '-' + self.id)     
        updatedXmlDescriptor = vmXmlDescriptor.getAsString()
        savedState.updateStoredVmDescription(updatedXmlDescriptor)
        
        # Restore a VM to the state indicated in the associated memory image file, in running mode.
        # The XML descriptor is given since some things have changed, though effectively it is not used here since
        # the memory image file has already been merged with this in the statement above.
        try:
            print "Resuming from VM image..."
            self.hypervisor.restoreFlags(savedState.savedStateFilename, self.xmlDescriptorString, libvirt.VIR_DOMAIN_SAVE_RUNNING)
        except libvirt.libvirtError as e:
            message = "Error resuming VM: %s for VM; error is: %s" % (str(self.id), str(e))           
            raise VirtualMachineException(message)            
        
        # Since this method does not return a pointer to the VM, we get it from another API function.
        try:
            self.connectToRunningInstance()
        except VirtualMachineException:
            # Something really weird happened, as we just started this VM, and no exceptions were thrown when starting it.
            raise VirtualMachineException('Could not connect to newly resumed VM with id %d. Descriptor: %s' % (self.id, updatedXmlDescriptor))
            
        # If a GUI was requested, start VNC and wait for the user to close the window.
        if(showVNC):
            self.startVncAndWait()
            
    ################################################################################################################
    # Finds a running VM with our id and loads that VM in our object.
    ################################################################################################################  
    def connectToRunningInstance(self):
        try:
            self.virtualMachine = self.hypervisor.lookupByUUIDString(self.id)
        except Exception as e:
            # This means the instance could not be found.
            print 'Error connecting to running instance: ' + str(e)
            raise VirtualMachineException('Instance %s could not be found by hypervisor.' % str(self.id))
            
    ################################################################################################################
    # Updates a given XML descriptor string with this VM's information, and stores it internally.
    ################################################################################################################  
    def __updateXmlDescriptorString(self, xmlDescriptorString):
        # Load the description of the VM.
        vmXmlDescriptor = VirtualMachineDescriptor(xmlDescriptorString)
              
        # Set the ID and name of the VM.
        # NOTE: This is what requires us to manually modify the saved memory image, to modify this UUID, since libvirt won't allow this change.
        vmXmlDescriptor.setUuid(self.id)
        vmXmlDescriptor.setName(self.prefix + '-' + self.id) 

        # Set the disk image in the description of the VM.
        vmXmlDescriptor.setDiskImage(self.diskImage.filepath, self.diskImage.type)        
        
        # Set the ports to redirect, if any, clearing any existing ones.
        vmXmlDescriptor.setPortRedirection(self.portMappings)
        
        # Update our internal XML string.
        self.xmlDescriptorString = vmXmlDescriptor.getAsString()
            
    ################################################################################################################
    # Pauses a VM and stores its memory state to a disk file. Also destroys the transient VM.
    # Returns the name of the file where the memory was saved to.
    ################################################################################################################          
    def suspendToFile(self, savedStateFile=None):
        try:
            # If no memory image was provided, we will define a name for it based on the disk image.
            if(savedStateFile == None):
                savedStateFile = self.getDefaultSavedStateFile()        
            savedState = vmsavedstate.VMSavedState(savedStateFile)        
            
            # We indicate that we want want to use as much bandwidth as possible to store the VM's memory when suspending.
            unlimitedBandwidth = 1000000    # In Gpbs
            self.virtualMachine.migrateSetMaxSpeed(unlimitedBandwidth, 0)
            
            # We actually pause the VM.
            result = self.virtualMachine.suspend()
            if(result == -1):
                raise VirtualMachineException("Cannot pause VM : %s", self.virtualMachine.name())
            
            # Store the VM's memory state to a disk image file.
            print "Storing VM memory state to file %s" % savedState.savedStateFilename
            result = 0
            try:
                result = self.virtualMachine.save(savedState.savedStateFilename)
                
                # We set the VM to None since, after saving, the VM goes away (we are handling transient VMs only in this class).
                self.virtualMachine = None
            except libvirt.libvirtError, e:
                raise VirtualMachineException(str(e))
            if result != 0:
                raise VirtualMachineException("Cannot save memory state to file %s", self.virtualMachine.name())
            
            return savedState.savedStateFilename
        except:
            # In case we failed, cleanup by destroying the VM, which is expected at the end of the method anyway.
            self.destroy()
            raise
        
    ################################################################################################################
    # Destroys the VM. 
    ################################################################################################################                  
    def destroy(self):
        if (not self.virtualMachine == None):
            print "Destroying VM..."
            self.closeSSHConnection()
            self.virtualMachine.destroy()
            self.virtualMachine = None
        self.hypervisor.close()

    ################################################################################################################
    # Returns the default filename for the saved state of a VM, which is based on the disk image path.
    ################################################################################################################     
    def getDefaultSavedStateFile(self):
        defaultSaveStateFilepath = vmsavedstate.VMSavedState.getCorrectFilepath(self.diskImage.filepath)
        return defaultSaveStateFilepath          
                
    ################################################################################################################
    # Opens an SSH session.
    ################################################################################################################       
    def openSSHConnection(self):
        if(self.sshHostPort != None):
            print('Connecting through SSH to port ' + str(self.sshHostPort))
            self.sshClient = vmssh.VmSshClient(self.sshHostPort)
        else:
            raise VirtualMachineException("No SSH port configured for connection.")
        
    ################################################################################################################
    # Closes an SSH session.
    ################################################################################################################       
    def closeSSHConnection(self):
        if(self.sshClient != None):
            print('Disconnecting from SSH.')
            self.sshClient.disconnect()
            self.sshClient = None
    
    ################################################################################################################
    # Uploads a file through SFTP to a running VM.
    # NOTE: destFilePath has to be a full file path, not only a folder.
    ################################################################################################################       
    def uploadFile(self, sourceFilePath, destFilePath):
        # Check if we are not already connected.
        if(self.sshClient == None):
            self.openSSHConnection()
        
        # Send the file.
        print('Sending file %s to %s.' % (sourceFilePath, destFilePath))
        self.sshClient.uploadFile(sourceFilePath, destFilePath)
        print('File sent.')
        
    ################################################################################################################
    # Sends a command through SSH to a running VM.
    ################################################################################################################       
    def executeCommand(self, command):       
        # Check if we are not already connected.
        if(self.sshClient == None):
            self.openSSHConnection()

        print('Sending command "%s".' % command)
        result = self.sshClient.executeCommand(command)
        print('Command sent.')
        return result

################################################################################################################
# Additional imports.
################################################################################################################

# Used to parse the XML for the VirtualMachineDescriptor.
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

################################################################################################################
# Represents an XML description of a VM.
################################################################################################################                 
class VirtualMachineDescriptor(object):                
                
    # The namespace and nodes used for QEMU parameters.
    qemuXmlNs = "http://libvirt.org/schemas/domain/qemu/1.0"
    qemuCmdLineNodeName = "{%s}commandline" % qemuXmlNs
    qemuArgNodeName = "{%s}arg" % qemuXmlNs
                
    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, xmlDescriptorString):
        # Load the XML root element from the XML descriptor string.
        self.xmlRoot = ElementTree.fromstring(xmlDescriptorString)
        
    ################################################################################################################ 
    # Returns an XML string with the contents of this VMDescriptor
    ################################################################################################################ 
    def getAsString(self):    
        xmlString = ElementTree.tostring(self.xmlRoot)
        return xmlString             
        
    ################################################################################################################
    # Sets the path to the main disk image.
    ################################################################################################################         
    def setDiskImage(self, newDiskImagePath, newDiskType):                    
        # Find the first disk in the description.
        diskElements = self.xmlRoot.findall('devices/disk')
        mainDiskImageNode = None
        mainDiskDriverNode = None
        for diskElement in diskElements:
            diskType = diskElement.attrib['device']
            if diskType == 'disk':
                mainDiskImageNode = diskElement.find('source')
                mainDiskDriverNode = diskElement.find('driver')
                break
    
        # Check if we found a disk.
        if mainDiskImageNode == None or mainDiskDriverNode == None:
            raise VirtualMachineException("No disk found in XML descriptor.")
        
        # Set the path to the new disk image.        
        mainDiskImageNode.set("file", os.path.abspath(newDiskImagePath))
        mainDiskDriverNode.set("type", newDiskType)
                
    ################################################################################################################
    # Sets the VM name.
    ################################################################################################################ 
    def setName(self, newName):
        nameElement = self.xmlRoot.find('name')
        if nameElement is None:
            raise VirtualMachineException("No name node found in XML descriptor.")
        nameElement.text = newName
    
    ################################################################################################################
    # Sets the VM id.
    ################################################################################################################ 
    def setUuid(self, newUUID):    
        uuidElement = self.xmlRoot.find('uuid')
        if uuidElement is None:
            raise VirtualMachineException("No UUID node found in XML descriptor.")            
        uuidElement.text = newUUID
    
    ################################################################################################################
    # Gets the VM id.
    ################################################################################################################ 
    def getUuid(self):    
        uuidElement = self.xmlRoot.find('uuid')
        if uuidElement is None:
            raise VirtualMachineException("No UUID node found in XML descriptor.")            
        return str(uuidElement.text)
    
    ################################################################################################################
    # Sets port redirection commands for qemu.
    ################################################################################################################ 
    def setPortRedirection(self, portMappings):
        # Get the node with qemu-related arguments.        
        qemuElement = self.xmlRoot.find(self.qemuCmdLineNodeName)
        
        # If the node was not there, add it.
        if qemuElement == None:
            qemuElement = Element(self.qemuCmdLineNodeName)
            self.xmlRoot.append(qemuElement)

        # Values for redirect arguments.
        portRedirectionCommand = '-redir'
        
        # First we will remove all redirections that contain either the host or guest port.
        qemuArgumentElements = qemuElement.findall(self.qemuArgNodeName)
        lastRedirElement = None
        for qemuArgument in qemuArgumentElements:
            # Get the actual value to check. 
            qemuArgumentValue = qemuArgument.get('value')
            
            # Store "redir" commands since, if we have to remove a redirection, we also have to remove this previous node.
            if(portRedirectionCommand in qemuArgumentValue):
                lastRedirElement = qemuArgument
                continue
            
            # We will assume that only redirections will have the :%d::%d format. If we find any argument
            # with this format and the host or guest ports redirected, we will remove it, along with
            # the previous redir command argument.
            #if(':%d::' % int(hostPort) in qemuArgumentValue) or ('::%d' % int(guestPort) in qemuArgumentValue):
            
            # We will assume that only redirection arguments have "tcp:" in them, and we will remove them all.
            if('tcp:' in qemuArgumentValue):
                qemuElement.remove(lastRedirElement)
                qemuElement.remove(qemuArgument)
                
            if('-usb' in qemuArgumentValue):
                qemuElement.remove(qemuArgument)

        # Now we setup the redirection for all the port mappings that were provided.
        for hostPort, guestPort in portMappings.iteritems():
            #break
            portRedirectionValue = 'tcp:%d::%d' % (int(hostPort), int(guestPort))        
            qemuElement.append(Element(self.qemuArgNodeName, {'value':portRedirectionCommand}))
            qemuElement.append(Element(self.qemuArgNodeName, {'value':portRedirectionValue}))
            #break

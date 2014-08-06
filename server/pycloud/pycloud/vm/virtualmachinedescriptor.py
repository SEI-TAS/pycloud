__author__ = 'jdroot'

# Used to parse the XML for the VirtualMachineDescriptor.
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from pycloud.pycloud.model.servicevm import VirtualMachineException
import os

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
    # Returns the port the VNC server is listening on, if any.
    ################################################################################################################
    def getVNCPort(self):
        vncPort = self.xmlRoot.find("devices/graphics").get("port")
        return vncPort    

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


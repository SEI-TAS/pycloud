    #!/usr/bin/env python
#       

################################################################################################################
# Imports.
################################################################################################################

# Used for argument handling.
import sys  

# Used to parse command-line arguments.
import argparse

# Manager of VM stuff.
import vm.storedvm
import servicevm.instancemanager
import servicevm.svmrepository
import servicevm.ssvmfactory

# For exceptions.
import vm.vmrepository

################################################################################################################
# Global constants.
################################################################################################################

# Valid commands.
CMD_CREATE_VM = "create"
CMD_RUN_VM = "run"
CMD_LIST_VM = "list"
CMD_TEST_SSH = "test_ssh"
CMD_MODIFY = "modify"
COMMAND_LIST = [CMD_CREATE_VM, CMD_RUN_VM, CMD_LIST_VM, CMD_TEST_SSH, CMD_MODIFY]

################################################################################################################
# Parse the basic commands.
################################################################################################################
def parseCommand():    
    # Check that we have a valid command.
    commandParser = argparse.ArgumentParser(description='Manage Service VMs.')
    commandParser.add_argument('command', choices=COMMAND_LIST)
    commandArguments = commandParser.parse_known_args()[0]
    command = commandArguments.command
    
    return command

################################################################################################################
# Parses the arguments for the ServiceVM creation command.    
################################################################################################################    
def parseCreateCommandArguments():
    # Check that we have the arguments for the overlay command.        
    parser = argparse.ArgumentParser(description='Create a Service VM.')
    parser.add_argument('-sourceImage', required=True, action='store',  help='The path to the source disk image to use for the VM.')
    parser.add_argument('-type', required=True, action='store',  help='The OS: Windows for Windows, Linux for Linux.')    
    parser.add_argument('-serviceId', required=True, action='store',  help='The id of the Service.')
    parser.add_argument('-name', required=True, action='store',  help='A name for the ServiceVM files.')
    parser.add_argument('-port', required=True, action='store',  help='The port the server will be listening on inside the Service VM.')   
    parsedArguments = parser.parse_known_args()[0]
    
    return parsedArguments

################################################################################################################
# Parses the arguments for the ServiceVM running command.    
################################################################################################################    
def parseRunVmCommandArguments():
    # Check that we have the arguments for the overlay command.        
    parser = argparse.ArgumentParser(description='Execute an instance of an existing Service VM.')
    parser.add_argument('-serviceId', required=True, action='store',  help='The id of the service in the service VM.')
    parsedArguments = parser.parse_known_args()[0]
    
    return parsedArguments


################################################################################################################
# Parses the arguments for the ServiceVM modification command.    
################################################################################################################    
def parseModifyVmCommandArguments():
    # Check that we have the arguments for the overlay command.        
    parser = argparse.ArgumentParser(description='Modifying an existing Service VM.')
    parser.add_argument('-serviceId', required=True, action='store',  help='The id of the service in the service VM.')
    parsedArguments = parser.parse_known_args()[0]
    
    return parsedArguments
################################################################################################################
# Parses the arguments for the SSH Test command.    
################################################################################################################    
def parseTestSshCommandArguments():
    # Check that we have the arguments for the overlay command.        
    parser = argparse.ArgumentParser(description='Test SSH on an exiting Server VM.')
    parser.add_argument('-serviceId', required=True, action='store',  help='The id of the service.')
    parser.add_argument('-sfilepath', required=True, action='store',  help='The file to send.')
    parser.add_argument('-dfilepath', required=True, action='store',  help='The file to store remotely.')
    parser.add_argument('-command', required=True, action='store',  help='The command to execute')
    parsedArguments = parser.parse_known_args()[0]
    
    return parsedArguments 

################################################################################################################
# Main entry point of the tool.
################################################################################################################
def main():
    
    command = parseCommand() 
    print 'Command: ' + command
    
    if(command == CMD_CREATE_VM):
        # Parse the commands for overlay creation and create it.
        arguments = parseCreateCommandArguments()
        
        try:
            # Create it.
            newStoredServiceVM = servicevm.ssvmfactory.StoredServiceVMFactory.createFromDiskImage(vmType=arguments.type,
                                                                             sourceDiskImageFilePath=arguments.sourceImage,
                                                                             serviceId=arguments.serviceId, 
                                                                             serviceVMName=arguments.name, 
                                                                             servicePort=arguments.port)
            
            # Store it in the repo.
            print "Saving ServiceVM."
            serviceVMRepository = servicevm.svmrepository.ServiceVMRepository()
            serviceVMRepository.addStoredVM(newStoredServiceVM)
            print "ServiceVM stored in repository."            
            
        except vm.storedvm.StoredVMException as e:
            print "Error creating Service VM: " + e.message       
    
    elif(command == CMD_RUN_VM):
        # Parse the commands for vm running and create it.
        arguments = parseRunVmCommandArguments()
        
        try:     
            # Run a VM with a VNC GUI.
            instanceMan = servicevm.instancemanager.ServiceVMInstanceManager()
            runningInstance = instanceMan.getServiceVMInstance(serviceId=arguments.serviceId,
                                                               showVNC=True)

            # After we unblocked because the user closed the GUI, we just kill the VM.
            instanceMan.stopServiceVMInstance(runningInstance.instanceId)
        except servicevm.instancemanager.ServiceVMInstanceManagerException as e:
            print "Error running Server VM: " + e.message
            
    elif(command == CMD_MODIFY):
        # Parse the commands for vm modification.
        arguments = parseModifyVmCommandArguments()
        
        try:     
            # Get the VM, and make it writeable.
            serviceId = arguments.serviceId
            serviceVMRepository = servicevm.svmrepository.ServiceVMRepository()
            storedServiceVM = serviceVMRepository.getStoredServiceVM(serviceId)
            storedServiceVM.unprotect()
            
            # Run the VM with GUI and store its state.
            defaultMaintenanceServiceHostPort = 16001
            runningSVM = servicevm.runningsvmfactory.RunningSVMFactory.createRunningVM(storedVM=storedServiceVM,
                                                                                       showVNC=True,
                                                                                       serviceHostPort=defaultMaintenanceServiceHostPort)
            runningSVM.suspendToFile()
            
            # Destroy the running VM.
            runningSVM.destroy()     
            
            # Make the stored VM read only again.
            storedServiceVM.protect()
        except servicevm.instancemanager.ServiceVMInstanceManagerException as e:
            print "Error modifying Server VM: " + e.message        
            
    elif(command == CMD_LIST_VM):
        try:
            # Get a list and print it.
            serviceVmRepo = servicevm.svmrepository.ServiceVMRepository()
            vmList = serviceVmRepo.getVMListAsString()
            print '\nService VM List:'
            print vmList
        except vm.vmrepository.VMRepositoryException as e:
            print "Error getting list of Server VMs: " + e.message
            
    elif(command == CMD_TEST_SSH):
        # Parse the commands for vm running and create it.
        arguments = parseTestSshCommandArguments()

        instanceMan = None
        runningInstance = None        
        try:
            # Create the manager and access the VM.
            instanceMan = servicevm.instancemanager.ServiceVMInstanceManager()
            runningInstance = instanceMan.getServiceVMInstance(serviceId=arguments.serviceId,
                                                               showVNC=False)
            
            # Send commands.
            runningInstance.uploadFile(arguments.sfilepath, arguments.dfilepath)
            result = runningInstance.executeCommand(arguments.command)
            print 'Result of command: ' + result
            
            # Close connection.
            runningInstance.closeSSHConnection()
            
        except servicevm.instancemanager.ServiceVMInstanceManagerException as e:
            print "Error testing ssh connection: " + e.message     
        finally:
            # Cleanup.
            if(instanceMan != None and runningInstance != None):
                instanceMan.stopServiceVMInstance(runningInstance.instanceId) 
                        

################################################################################################################
# The call to the actual main function.
################################################################################################################
if __name__ == "__main__":
    status = main()
    sys.exit(status)    

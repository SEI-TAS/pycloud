#!/usr/bin/env python
#       

################################################################################################################
# Imports.
################################################################################################################

# Used to parse command-line arguments.
import argparse

# For SVM Cache management.
from pycloud.pycloud.servicevm import cachemanager

# For config management.
from pycloud.pycloud.utils import config
from pycloud.pycloud import cloudlet

################################################################################################################
# Global constants.
################################################################################################################

# Configuration.
MAIN_CONFIG_FILE = "development.ini"

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
    # Load the config. (TODO: this is a hacky way of sharing the devini file with Pylons).
    # NOTE: here pycloud.util.config is creating a dictionary of configurations in the default
    # section of development.ini. This is similar to what is created by Pylons when loading
    # a configuraton, tough pylons.config has more information. Since Cloudlet uses only the basic
    # dictionary values, the dictionary we load here is equivalent to the pylons.config object.
    configuration = config.Configuration.getDefaults(MAIN_CONFIG_FILE)
    cloudletConfig = cloudlet.Cloudlet(configuration)
    
    # Create the cache manager.
    svmCacheManager = cachemanager.ServiceVMCacheManager(cloudletConfig)
    
    # Get the command.
    command = parseCommand() 
    print 'Command: ' + command
    
    # Choose the action depending on the command.
    if(command == CMD_CREATE_VM):
        # Parse the commands for overlay creation and create it.
        arguments = parseCreateCommandArguments()
        svmCacheManager.createServiceVM(arguments.type, arguments.sourceImage, arguments.serviceId, arguments.name, arguments.port)
    
    elif(command == CMD_RUN_VM):
        # Parse the commands for vm running and create it.
        arguments = parseRunVmCommandArguments()
        svmCacheManager.runServiceVMInstance(arguments.serviceId)
            
    elif(command == CMD_MODIFY):
        # Parse the commands for vm modification.
        arguments = parseModifyVmCommandArguments()
        svmCacheManager.modifyServiceVM(arguments.serviceId)
            
    elif(command == CMD_LIST_VM):
        svmCacheManager.listServiceVMs()
            
    elif(command == CMD_TEST_SSH):
        # Parse the commands for vm running and create it.
        arguments = parseTestSshCommandArguments()
        svmCacheManager.testSSH(arguments.serviceId, arguments.sfilepath, arguments.dfilepath, arguments.command)

#!/usr/bin/env python
#       

# To generate random port numbers.
import random

################################################################################################################
# Handles TCP ports.
################################################################################################################
class PortManager(object):
    
    # Stores a list of ports in use.
    portsInUse = {}
    
    ################################################################################################################  
    # Generate a random port number which is available (in terms of this manager not using it). There is no check to
    # see if another process is using the port.
    ################################################################################################################ 
    @staticmethod  
    def generateRandomAvailablePort():
        # The range of ports were we will take a port from.
        rangeStart = 10000
        rangeEnd = 60000
        
        # Check if we still have ports available.
        if(len(PortManager.portsInUse) >= (rangeEnd - rangeStart)):
            raise ServiceVMInstanceManagerException("There are no ports available.")
        
        # This loop will eventually find an available port, since if all of them are in use, the check above would
        # have detected it. In practice, this loop will almost always run once, since we will not be handling that many
        # running instances to generate collisions.
        port = 0
        while(True):
            # Get a new random port and check if it is in use.
            port = random.randint(rangeStart, rangeEnd)
            if(not port in PortManager.portsInUse):
                # If the port is available, stop looking for more ports.
                PortManager.portsInUse[port] = True
                break

        return port
    
    ################################################################################################################  
    # Marks a given port as cleared.
    ################################################################################################################ 
    @staticmethod  
    def freePort(port):
        PortManager.portsInUse.pop(port, None)

    ################################################################################################################  
    # Marks all ports as free.
    ################################################################################################################ 
    @staticmethod  
    def clearPorts():
        PortManager.portsInUse.clear()
        
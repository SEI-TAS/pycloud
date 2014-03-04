#!/usr/bin/env python
#       

# Used to start external processes.
import subprocess

################################################################################################################
#
################################################################################################################
class VNCClient(object):   
    # Command used to connect to VNC tool, as well as default port.
    VNC_COMMAND = 'gvncviewer'
    VNC_CONN_ARG = "localhost:%d"
    VNC_DEFAULT_PORT = 5900

    ################################################################################################################
    # Starts a VNC connection, and waits till the user closes the VNC window. 
	# Returns true if everything went ok, or false if there was a problem creating the VNC connection or if it
	# was interrupted.
    ################################################################################################################        
    def connectAndWait(self, vncPort):
        # Starts VNC GUI in a separate process.
        try:
            vncCommandArguments = self.__getVncCommand(vncPort)
            vncPipe = subprocess.PIPE        
            vncProcess = subprocess.Popen(vncCommandArguments, shell=True, stdin=vncPipe, stdout=vncPipe, stderr=vncPipe)
        except Exception as e:
            print "Error creating VNC process: " + e.message
            return False
        
        # Wait until the VNC window is closed.
        try:            
            vncProcess.wait()
        except KeyboardInterrupt:
            # If the user interrupts the process when VNC is open, we abort by destroying the VM.
            print "[INFO] Keyboard interrupt while waiting for VNC to be closed."
            return False
        
        return True        
        
    ################################################################################################################
    # Returns the VNC command to use to connect to the GUI. Only supports gvncviewer for now.
    ################################################################################################################          
    def __getVncCommand(self, vncPort):
        # First we get the display number for gvncviewer.
        displayNumber = 0
        try:
			# GVNCviewer uses not port, but display number, starting at 0. We have to substract the port the VM is            
            # using from the default port to get this relative display number.
            displayNumber = int(vncPort) - self.VNC_DEFAULT_PORT
        except AttributeError as e:
            print "Warning, Possible VNC port error:%s\n" % str(e)
        
        # Now we create the command itself.
        hostArgument = self.VNC_CONN_ARG % displayNumber
        vncFullCommand = self.VNC_COMMAND + ' ' +  hostArgument
        #print self.VNC_COMMAND + ' ' + hostArgument              
            
        return vncFullCommand

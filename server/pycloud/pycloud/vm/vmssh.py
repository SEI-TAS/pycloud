#!/usr/bin/env python
#       

# For SSH connections.
import paramiko
       
################################################################################################################
# SSH client to a runniv VM.
################################################################################################################
class VmSshClient(object):

    # The host will be localhost since we are assuming the VMs are using port forwarding.
    HOST = "localhost"
    
    # Default user and password.
    DEFAULT_USER = "cloudlet"    
    DEFAULT_PASSWORD = "cloudlet"
    
    # Max size of the return value for commands.
    MAX_RETURN_VALUE = 4096
    
    # The SSH connection.
    sshConn = None

    ################################################################################################################
    # Connects to a VM through SSH.
    ################################################################################################################           
    def __init__(self, sshPort):
        # Connect with authentication.        
        self.sshConn = paramiko.SSHClient()
        self.sshConn.load_system_host_keys()
        self.sshConn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshConn.connect(hostname = self.HOST, port = sshPort, username = self.DEFAULT_USER, password = self.DEFAULT_PASSWORD)
                
    ################################################################################################################
    # Uploads a file through SFTP to a running VM.
    # NOTE: destFilePath has to be a full file path, not only a folder.
    ################################################################################################################       
    def uploadFile(self, sourceFilePath, destFilePath):
        # Establish an SFTP session.        
        sftp = self.sshConn.open_sftp()
        
        # Upload the file.
        print 'Transfering file...'
        sftp.put(sourceFilePath, destFilePath)
        print 'File transfered.'
       
    ################################################################################################################
    # Executes a command on a VM through SSH.
    ################################################################################################################              
    def executeCommand(self, command):
        # Send the command and get the result.
        #sshStdin, sshStdout, sshStderr = self.sshConn.exec_command(command)  # @UnusedVariable
        channel = self.sshConn.invoke_shell()
        sshStdin = channel.makefile('wb')
        sshStdout = channel.makefile('rb')
        
        sshStdin.write('''
        ''' + command + '''
        exit
        ''')
            
        # Return whatever the command returned.            
        returnValue = sshStdout.read()
        
        sshStdin.close()
        sshStdout.close()
        
        return returnValue       

    ################################################################################################################
    # Ends the SSH session.
    ################################################################################################################              
    def disconnect(self):
        self.sshConn.close()
        self.sshConn = None
        
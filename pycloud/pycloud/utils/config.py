#!/usr/bin/env python
#       

# To load the configuration.
import ConfigParser

################################################################################################################
# Stores the configuration.
################################################################################################################
class Configuration(object):
    
    # The default config file.
    CONFIGURATION_FILE = './cloudlet.conf'
    
    # The parser used to get the parameters.
    parser = None
        
    ################################################################################################################
    # Creates a parser for the default config file, if it wasn't loaded before.
    ################################################################################################################
    @staticmethod
    def loadConfiguration():
        if(Configuration.parser == None):
            print 'Loading config from %s ' % Configuration.CONFIGURATION_FILE 
            Configuration.parser = ConfigParser.ConfigParser()            
            Configuration.parser.read(Configuration.CONFIGURATION_FILE)        
        
    ################################################################################################################
    # Returns a paramter from the configuration.
    ################################################################################################################
    @staticmethod
    def getParam(section, paramKey):
        Configuration.loadConfiguration()
        return Configuration.parser.get(section, paramKey)   

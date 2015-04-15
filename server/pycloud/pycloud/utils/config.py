#!/usr/bin/env python
#       

# To load the configuration.
import ConfigParser as configparser

################################################################################################################
# Stores the configuration.
################################################################################################################
class Configuration(object):
    
    # The default config file.
    CONFIGURATION_FILE = 'cloudlet.conf'
    
    # The parser used to get the parameters.
    parser = None
        
    ################################################################################################################
    # Creates a parser for the default config file, if it wasn't loaded before.
    ################################################################################################################
    @staticmethod
    def loadConfiguration(configFile):
        if(Configuration.parser == None):
            if(configFile == ""):
                configFile = Configuration.CONFIGURATION_FILE
            print 'Loading config from %s ' % configFile
            Configuration.parser = configparser.ConfigParser()            
            Configuration.parser.readfp(open(configFile))        
        
    ################################################################################################################
    # Returns a dict with the default values.
    ################################################################################################################
    @staticmethod
    def getDefaults(configFile=""):
        Configuration.loadConfiguration(configFile)
        return Configuration.parser.defaults()

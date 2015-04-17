# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

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

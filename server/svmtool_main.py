#!/usr/bin/env python
#       

# Used for status handling.
import sys  

from pycloud.pycloud.vm import svmtool

################################################################################################################
# The call to the actual main function.
################################################################################################################
if __name__ == "__main__":
    status = svmtool.main()
    sys.exit(status)    

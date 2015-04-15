#!/usr/bin/env python
#       

################################################################################################################
# Various ajax utility functions.
################################################################################################################

# Default return messages for ajax requests.
JSON_OK = {"STATUS": "OK"}
JSON_NOT_OK = {"STATUS": "NOT OK", "error": ""}

################################################################################################################
# Prints and returns the given error through a json appropriate dict.
################################################################################################################
def show_and_return_error_dict(error_message):
    print error_message
    error_dict = JSON_NOT_OK
    error_dict['error'] = error_message
    return error_dict
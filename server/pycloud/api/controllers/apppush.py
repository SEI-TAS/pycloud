import logging

# Pylon imports.
from pylons import request
from pylons import g
from pylons.controllers.util import abort
from paste import fileapp

# For serializing JSON data.
import json

# To handle basic OS stuff.
import os

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.utils import timelog
from pycloud.pycloud.model import App

log = logging.getLogger(__name__)

################################################################################################################
# Class that handles Service VM related HTTP requests to a Cloudlet.
################################################################################################################
class AppPushController(BaseController):

    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})    

    ################################################################################################################
    # Called to get a list of apps available at the server.
    ################################################################################################################
    def GET_getList(self):
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request for stored apps received.")
            
        apps = App.find()
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        return apps
        
    ################################################################################################################
    # Called to get an app from the server.
    ################################################################################################################
    def GET_getApp(self):
        app_id = request.params.get('app_id', None)
        if not app_id:
            # If we didnt get a valid one, just return an error message.
            print "No app name to be retrieved was received."
            abort(400, '400 Bad Request - must provide app_id')
        
        print '\n*************************************************************************************************'    
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request to push app received.")

        app = App.by_id(app_id)
        if not app:
            print "No app found for specified id"
            abort(404, '404 Not Found - app with id "%s" was not found' % app_id)
                                
        # Log that we are responding.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()                                

        # Create a FileApp to return the APK to download. This app will do the actually return execution;
        # this makes the current action a middleware for this app in WSGI definitions.
        # The content_disposition header allows the file to be downloaded properly and with its actual name.
        fapp = fileapp.FileApp(app.apk_file, content_disposition='attachment; filename="' + app.file_name() + '"')

        # Send the response, serving the apk file back to the client.
        return fapp(request.environ, self.start_response)

import logging
import json
import urllib
import os.path
import shutil

from bson import ObjectId

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML
from webhelpers.html import literal

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.manager.lib.pages import AppsPage
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.model import App, Service

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class AppsController(BaseController):

    JSON_OK = {"STATUS" : "OK" }
    JSON_NOT_OK = { "STATUS" : "NOT OK"}

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_list()

    ############################################################################################################
    # Shows the list of stored Apps.
    ############################################################################################################
    def GET_list(self):
        # Mark the active tab.
        c.apps_active = 'active'    
        
        # Create the actual page.
        page = AppsPage()
        
        # Setup the page to render.
        # page.form_values = {}
        # page.form_errors = {}
    
        # Get a list of existing stored apps.
        page.apps = App.find()

        # Create an item list with the info to display.
        # grid_items = []
        # for app in apps:
        #     new_item = {'name': app.name,
        #                'service_id': app.service_id,
        #                'description': app.description,
        #                'version': app.app_version,
        #                'min_android_version': app.min_android_version,
        #                'apk_file': app.apk_file,
        #                'actions': 'Edit',
        #                'id': app._id}
        #     grid_items.append(new_item)
        #
        # # Create and fomat the grid.
        # appsGrid = Grid(grid_items, ['name', 'service_id', 'description', 'version', 'min_android_version', 'apk_file', 'actions'])
        # appsGrid.column_formats["actions"] = generateActionButtons
        
        # Prepare service list.
        page.stored_services = {}
        services = Service.find()
        for service in services:
            page.stored_services[service.service_id] = service.service_id
        
        # Pass the grid and render the page.
        # page.appsGrid = appsGrid
        return page.render()

    ############################################################################################################
    # Gets data for an app.
    ############################################################################################################
    @asjson    
    def POST_get_data(self):
        # Get the data for the given app.
        print 'App data request received, data: ' + request.params.get('appId')        
        app_id = ObjectId(request.params.get('appId'))
        app = App.by_id(app_id)
        
        if not app:
            # If there was a problem getting the app to update, return a json-formated error.
            print 'Error getting app data: app was not found'
            return self.JSON_NOT_OK        

        return app

    ############################################################################################################
    # Creates or updates an app.
    ############################################################################################################
    @asjson
    def POST_edit(self):
        try:
            # Create a new app object if we are adding, or get the current if we are updating.
            if request.params.get('appId') == '':
                print 'Creating new app'
                app = App()
            else:
                # Get the existing app from the DB, if it can be found.
                print 'Updating app with id ' + request.params.get('appId')
                app = App.by_id(ObjectId(request.params.get('appId')))                
                if not app:
                    # If there was a problem getting the app to update, return a json-formated error.
                    print 'Error getting app to modify: app was not found'
                    return self.JSON_NOT_OK
            
            # Set the values for all the apps' fields.
            app.name = request.params.get('name')
            app.service_id = request.params.get('serviceId')
            app.description = request.params.get('description')
            app.app_version = request.params.get('version')
            app.package_name = request.params.get('package')
            app.tags = request.params.get('tags')
            if app.tags:
                app.tags = app.tags.split(',')
            else:
                app.tags = []
            app.min_android_version = request.params.get('minOsVersion')
            
            # Check if we are uploading a new apk.
            if(request.params.get('appNewFile') != None):
                print 'Updating file: ' + str(request.params.get('appNewFile'))
                app.apk_file = os.path.join(os.path.abspath(g.cloudlet.appFolder), request.params.get('appNewFile').filename)
                
                # Store the file in the folder first.
                apk_file_dest = open(app.apk_file, 'w')            
                shutil.copyfileobj(request.params.get('appNewFile').file, apk_file_dest)
                
                # TODO add these to the DB. md5 will have to be calculated.
                app.md5sum = None
            
            # Save the new/updated app to the DB.
            app.save()
            
            if(request.params.get('appNewFile') != None):
                # Rename the app file to be unique and update its filename in the DB.
                new_apk_filename = os.path.join(os.path.dirname(app.apk_file), str(app._id) + '-' + os.path.basename(app.apk_file))
                os.rename(app.apk_file, new_apk_filename)
                app.apk_file = new_apk_filename
                app.save()
            
            print 'App data stored.'
        except Exception as e:
            # If there was a problem creating the app, return a json-formated error.
            print 'Error creating App: ' + str(e)
            return self.JSON_NOT_OK
        
        # Everything went well.
        print 'Returning success'
        return self.JSON_OK   

    ############################################################################################################
    # Removes a stored app.
    ############################################################################################################
    @asjson       
    def POST_remove(self):
        # Parse the body of the request as JSON into a python object.
        # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
        parsedJsonString = urllib.unquote(request.body)[:-1]
        fields = json.loads(parsedJsonString)
        print 'App removal request received, data: ' + parsedJsonString        
        
        try:
            # Remove the app.
            appId = ObjectId(fields['appId'])
            app = App.find_and_remove(appId)
            
            # Try to remove the app file.
            if(os.path.isfile(app.apk_file)):
                os.remove(app.apk_file)
            
            # Check if we succeeded.
            if app:
                print 'App removed.'
            else:
                print 'Error removing app: app was not found.'
                return self.JSON_NOT_OK                
        except Exception as e:
            print 'Error removing App: ' + str(e)
            return self.JSON_NOT_OK
        
        # Everything went well.
        return self.JSON_OK        

############################################################################################################
# Helper function to generate buttons to edit or delete apps.
############################################################################################################        
def generateActionButtons(col_num, i, item):
    # Link and button to edit the app.
    getAppDataURL = h.url_for(controller='apps', action='get_data')
    editButton = HTML.button("Edit App", onclick=literal("showEditAppModal('" + getAppDataURL + "', '" + str(item["id"]) + "')"), class_="btn btn-primary")

    # Ajax URL to remove the app.
    removeAppURL = h.url_for(controller='apps', action='remove')
    removeButton = HTML.button("Remove App", onclick="removeAppConfirmation('" + removeAppURL + "', '" + str(item["id"])  + "', '" + str(item["name"]) + "');", class_="btn btn-primary btn")
    
    # Render the buttons.
    return HTML.td(editButton + literal("&nbsp;") + removeButton  )       

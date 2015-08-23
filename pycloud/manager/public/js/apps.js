/*
KVM-based Discoverable Cloudlet (KD-Cloudlet) 
Copyright (c) 2015 Carnegie Mellon University.
All Rights Reserved.

THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.

Released under a modified BSD license, please see license.txt for full terms.
DM-0002138

KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
MiniMongo
Copyright (c) 2010-2014, Steve Lacy 
All rights reserved. Released under BSD license.
https://github.com/MiniMongo/minimongo/blob/master/LICENSE

Bootstrap
Copyright (c) 2011-2015 Twitter, Inc.
Released under the MIT License
https://github.com/twbs/bootstrap/blob/master/LICENSE

jQuery JavaScript Library v1.11.0
http://jquery.com/
Includes Sizzle.js
http://sizzlejs.com/
Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
Released under the MIT license
http://jquery.org/license
*/

/////////////////////////////////////////////////////////////////////////////////////
// Clears all data from the new/edit modal and shows it.
/////////////////////////////////////////////////////////////////////////////////////
function showNewAppModal()
{
    // Update texts.
    $('#edit-modal-title').text('Create New App');
    $('#edit-app-button').text('Create');    
 
    // Clear all fields.
    var appForm = $('#new-app-form');    
    appForm.find('#appId').val('');
    appForm.find('#appName').val('');
    appForm.find('#appDescription').val('');
    appForm.find('#appServiceId').val('');
    appForm.find('#appVersion').val('');
    appForm.find('#appPackage').val('');
    appForm.find('#appTags').val('');
    appForm.find('#appOSVersion').val('');
    appForm.find('#appNewFile').val('');
    
    // Show the modal.
    $('#modal-new-app').modal('show');    
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to load data in a modal before editing it.
/////////////////////////////////////////////////////////////////////////////////////
function showEditAppModal(getDataURL, id)
{
    // Update texts.
    $('#edit-modal-title').text('Edit App');
    $('#edit-app-button').text('Modify');    
    
    // Prepare the id to be sent (to get data).
    app = {};
    app.appId = id;
    
    // Handler to load data when received.
    var successHandler = function(app_info) {
        // Set all the fields in the form.
        var appForm = $('#new-app-form');
        appForm.find('#appId').val(app_info._id);
        appForm.find('#appName').val(app_info.name);
        appForm.find('#appDescription').val(app_info.description);
        appForm.find('#appServiceId').val(app_info.service_id);
        appForm.find('#appVersion').val(app_info.app_version);
        appForm.find('#appPackage').val(app_info.package_name);
        appForm.find('#appTags').val(app_info.tags);
        appForm.find('#appOSVersion').val(app_info.min_android_version);
        
        // Clear the file field, since file inputs can't be populated.
        appForm.find('#appNewFile').val('');

        // Show the modal.
        $('#modal-new-app').modal('show');
    };
    
    // Do the post to get data and load the modal.
    ajaxSimplePost(getDataURL, app, "Loading Data", successHandler);
}


/////////////////////////////////////////////////////////////////////////////////////
// Function to add or edit an app.
/////////////////////////////////////////////////////////////////////////////////////
function createApp()
{
    // Create an app object from the modal info.
    var appForm = $('#new-app-form');    
    newApp = {};
    newApp.appId = appForm.find('#appId').val();
    newApp.name = appForm.find('#appName').val();
    newApp.description = appForm.find('#appDescription').val();
    newApp.serviceId = appForm.find('#appServiceId').val();
    newApp.version = appForm.find('#appVersion').val();
    newApp.package = appForm.find('#appPackage').val();
    newApp.tags = appForm.find('#appTags').val();
    newApp.minOsVersion = appForm.find('#appOSVersion').val();
    newApp.filename = appForm.find('#appNewFile').val();
    
    // Validate that minimum data is there.
    var newAppModal = $('#modal-new-app');
    if(!validateMandatoryField(newApp.name, "App Name", newAppModal)) return false;
    if(!validateMandatoryField(newApp.serviceId, "Service Id", newAppModal)) return false;
    
    // File is only mandatory when creating (no need to change it when modifying).
    if(newApp.appId == '')
        if(!validateMandatoryField(newApp.filename, "APK File", newAppModal)) return false;
    
    // Check if we are adding or editing.
    if(newApp.appId == '')
        dialogText = "Creating App";
    else
        dialogText = "Updating App";
   
    // Post through ajax and reload with changes.  
    var postUrl = appForm.attr('action');
    if(newApp.filename != '')
        ajaxFilePost(postUrl, newApp, dialogText, reloadPage, "appNewFile", newAppModal);
    else
        ajaxSimplePost(postUrl, newApp, dialogText, reloadPage, newAppModal);
        
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to confirm to remove an app.
/////////////////////////////////////////////////////////////////////////////////////
function removeAppConfirmation(removeUrl, app_id, app_name)
{
    // Ask for confirmation.
    BootstrapDialog.confirm('Are you sure you want to delete <strong>'+app_name+'</strong>?', function(result){
            if(result) {
                removeApp(removeUrl, app_id);
            }
        });
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to remove an app.
/////////////////////////////////////////////////////////////////////////////////////
function removeApp(removeUrl, id)
{
    // Prepare the id to be sent.
    app = {};
    app.appId = id;
    
    // Post through ajax and reload with changes.
    ajaxSimplePost(removeUrl, app, "Removing App", reloadPage);
}

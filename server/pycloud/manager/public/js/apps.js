
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
    newApp.fileName = appForm.find('#appFilename').val();
    jsonData = JSON.stringify(newApp);
    
    // Check fi we are adding or editing.
    if(newApp.appId == '')
        dialogText = "Creating App";
    else
        dialogText = "Updating App";
    
    // Post through ajax and reload with changes.
    var newAppModal = $('#modal-new-app');    
    var postUrl = appForm.attr('action');    
    ajaxPostAndReload(postUrl, jsonData, dialogText, newAppModal);    
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Clears all data from the new/edit modal and shows it.
/////////////////////////////////////////////////////////////////////////////////////
function showNewAppModal()
{
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
    
    // Update texts.
    $('#edit-modal-title').text('Create New App');
    $('#edit-app-button').text('Create');
    
    // Show the modal.
    $('#modal-new-app').modal('show');    
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to load data in a modal before editing it.
/////////////////////////////////////////////////////////////////////////////////////
function loadAppData(getDataURL, id)
{
    // Update texts.
    $('#edit-modal-title').text('Edit App');
    $('#edit-app-button').text('Edit');    
    
    // Get info from the modal.
    var appForm = $('#new-app-form');
    var newAppModal = $('#modal-new-app'); 
    
    // Prepare the id to be sent.
    app = {};
    app.appId = id;
    jsonData = JSON.stringify(app);    

    // Send the ajax request to start the VNC window.
    $.ajax({
        url: getDataURL,
        type: 'POST',
        dataType: 'json',
        data: jsonData,      
        success: function( resp ) {           
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(resp))
            {
                showAndLogErrorMessage('App information could not be retrieved.', '', '', newAppModal);
            }
            else
            {
                // Update fields with the received app info.
                var jsonData = JSON.stringify(resp);
                var parsedJsonData = $.parseJSON(jsonData);
                console.log(parsedJsonData);
                app_info = parsedJsonData;
                
                // Set all the fields.
                appForm.find('#appId').val(app_info._id);
                appForm.find('#appName').val(app_info.name);
                appForm.find('#appDescription').val(app_info.description);
                appForm.find('#appServiceId').val(app_info.service_id);
                appForm.find('#appVersion').val(app_info.app_version);
                appForm.find('#appPackage').val(app_info.package_name);
                appForm.find('#appTags').val(app_info.tags);
                appForm.find('#appOSVersion').val(app_info.min_android_version);
                //appForm.find('#appFilename').val(app_info.apk_file);
        
                // Show the modal.
                $('#modal-new-app').modal('show');
            }
        },
        error: function( req, status, err ) {
            showAndLogErrorMessage('App information could not be retrieved.', status, err, newAppModal);
      }
    });
    
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
    jsonData = JSON.stringify(app);
    
    // Post through ajax and reload with changes.
    ajaxPostAndReload(removeUrl, jsonData, "Removing App");
}

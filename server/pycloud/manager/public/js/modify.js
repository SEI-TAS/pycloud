
/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to create an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openCreateVNC()
{
    // Show progress bar.
    var dialog = WaitDialog("Starting and Connecting to Service VM");
    dialog.show();
    
    // Get the modal div, which will be used later for alerts.
    var modalDiv = $('#modal-new-servicevm');
    
    // Get basic information about the form with the new svm.
    var formSVM = $('#new-svm-form');
    var serviceForm = $('#service-form');
    var actionURL = formSVM.attr('action');
    var source = formSVM.find('#sourceDiskImage');
    
    // Get all the edited fields of the svm.
    var svm_info = {};
    svm_info.source = formSVM.find('#sourceDiskImage').val();
    svm_info.type = formSVM.find('#osType').val();
    svm_info.port = serviceForm.find('#servicePort').val();
    svm_info.serviceId = serviceForm.find('#serviceID').val();
    jsonData = JSON.stringify(svm_info);

    // Send the ajax request to start the VNC window.
    $.ajax({
        url: actionURL,
        type: 'POST',
        dataType: 'json',
        data: jsonData,      
        success: function( resp ) {
            // Parse the response into a JSON structure.
            jsonData = JSON.stringify(resp);
            console.log(jsonData);
            parsedJsonData = $.parseJSON(jsonData);
            
            // Check if we got an error.
            if(parsedJsonData.hasOwnProperty('STATUS') && parsedJsonData.STATUS=='NOT OK')
            {
                // Dismiss the waiting dialog.
                dialog.hide();
                
                // Notify about the error.
                console.log( 'Something went wrong' );
                var alert = Alert('danger', 'Stored Service VM could not be created.', modalDiv);
                alert.show();
            }
            else
            {
                // Update Stored SVM fields with new SVM info.
                storedSVMData = parsedJsonData;
                ssvmFolder = $('#vmStoredFolder');
                ssvmFolder.val(storedSVMData.FOLDER);  
                ssvmDiskImagePath = $('#vmDiskImageFile');
                ssvmDiskImagePath.val(storedSVMData.DISK_IMAGE);
                ssvmStateImagePath = $('#vmStateImageFile');
                ssvmStateImagePath.val(storedSVMData.STATE_IMAGE);
                
                // Upate the buttons to reflect that we can now modify the SVM.
                $('#new-svm-button').prop('disabled', true);
                $('#modify-svm-button').prop('disabled', false);      
        
                // Dismiss the waiting dialog and the modal.
                dialog.hide();
                $('#modal-new-servicevm').modal('hide');
                
                // Notify that the process was successful.
                console.log( 'Service VM was created successfully.');        
                var alert = Alert('success', 'Stored Service VM was created successfully.', null);
                alert.show();
            }
        },
        error: function( req, status, err ) {
            // Dismiss the waiting dialog.
            dialog.hide();
            
            // Notify about the error.
            console.log( 'Something went wrong', status, err );
            var alert = Alert('danger', 'Stored Service VM could not be created.', modalDiv);
            alert.show();        
      }
    });
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openEditVNC(vncUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Starting and Connecting to Service VM");
    dialog.show();
    
    // Add the service ID to the URL.
    serviceId = $('#serviceID').val();
    vncUrl = vncUrl + "/" + serviceId;

    // Send the ajax request to start the VNC window.
    $.ajax({
      url: vncUrl,
      dataType: 'json',
      success: function( resp ) {
        // Notify that the process was successful.
        dialog.hide();
        var alert = Alert('success', 'Stored Service VM was modified successfully.', null);
        alert.show();
        console.log( 'Service VM was modified successfully.');        
      },
      error: function( req, status, err ) {
            // Dismiss the waiting dialog.
            dialog.hide();
            
            // Notify about the error.
            console.log( 'Something went wrong', status, err );
            var alert = Alert('danger', 'Stored Service VM could not be opened for modification.', null);
            alert.show();       
      }
    });
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to show a notification of a successful edit.
/////////////////////////////////////////////////////////////////////////////////////
function showEditSuccess()
{
    var alert = Alert('success', 'Service was modified successfully.');
    alert.show();
}

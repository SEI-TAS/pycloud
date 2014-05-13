
/////////////////////////////////////////////////////////////////////////////////////
// Checks that the minimum inputs have been submitted.
/////////////////////////////////////////////////////////////////////////////////////
function validateSubmission()
{
    // Get all the edited fields of the svm.
    var svm_info = {};
    svm_info.serviceId = $('#serviceID').val();
    svm_info.port = $('#servicePort').val();
    svm_info.folder = $('#vmStoredFolder').val();
    
    // Validate that we have all the necessary info.
    var errorHeader = 'You must enter a value for ';
    var errorMsg = '';
    if(svm_info.serviceId == '')
        errorMsg = errorHeader + ' service id.';
    else if(svm_info.port == '')
        errorMsg = errorHeader + ' service port.';
    //else if(svm_info.folder == '')
    //    errorMsg = 'You must create a Service VM.';
        
    // If an input is missing, notify the user and stop the process.
    if(errorMsg != '')
    {
        showAndLogErrorMessage(errorMsg);
        return false;
    }        
        
    // If everything is ok, submit the form.
    var serviceForm = $('#service-form');    
    serviceForm.submit();
    return true;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to create an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openCreateVNC()
{
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
    
    // Validate that we have all the necessary info.
    var errorHeader = 'You must enter a value for ';
    var errorMsg = '';
    console.log(jsonData);
    if(svm_info.source == '')
        errorMsg = errorHeader + ' source disk image.';
    else if(svm_info.serviceId == '')
        errorMsg = errorHeader + ' service id.';
    else if(svm_info.port == '')
        errorMsg = errorHeader + ' service port.';
        
    // If an input is missing, notify the user and stop the process.
    if(errorMsg != '')
    {
        showAndLogErrorMessage(errorMsg, '', '', modalDiv);
        return;
    }
    
    // Show progress bar.
    var dialog = WaitDialog("Starting and Connecting to Service VM");
    dialog.show();    

    // Send the ajax request to start the VNC window.
    $.ajax({
        url: actionURL,
        type: 'POST',
        dataType: 'json',
        data: jsonData,      
        success: function( resp ) {           
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(resp))
            {
                // Dismiss the waiting dialog and notify the error.
                dialog.hide();
                showAndLogErrorMessage('Stored Service VM could not be created.', '', '', modalDiv);
            }
            else
            {
                // Update Stored SVM fields with new SVM info.
                var jsonData = JSON.stringify(resp);
                var parsedJsonData = $.parseJSON(jsonData);
                storedSVMData = parsedJsonData;
                ssvmFolder = $('#vmStoredFolder');
                ssvmFolder.val(storedSVMData.FOLDER);  
                ssvmDiskImagePath = $('#vmDiskImageFile');
                ssvmDiskImagePath.val(storedSVMData.DISK_IMAGE);
                ssvmStateImagePath = $('#vmStateImageFile');
                ssvmStateImagePath.val(storedSVMData.STATE_IMAGE);
                
                // Upate the buttons to reflect that we can now modify the SVM.
                $('#new-svm-button').prop('style', 'display:none;');
                $('#modify-svm-button').prop('style', 'display:inline;');      
        
                // Dismiss the waiting dialog and the modal.
                dialog.hide();
                $('#modal-new-servicevm').modal('hide');
                
                // Notify that the process was successful.
                showAndLogSuccessMessage('Stored Service VM was created successfully.');
            }
        },
        error: function( req, status, err ) {
            // Dismiss the waiting dialog and notify.
            dialog.hide();
            showAndLogErrorMessage('Stored Service VM could not be created.', status, err, modalDiv);
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
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(resp))
            {
                // Dismiss the waiting dialog and notify the error.
                dialog.hide();
                showAndLogErrorMessage('There was a problem opening the Stored Service VM for modification.');                
            }
            else
            {
                // Dismiss the waiting dialog and notify the success.
                dialog.hide();
                showAndLogSuccessMessage('Stored Service VM was modified successfully.');
            }
      },
      error: function( req, status, err ) {
            // Dismiss the waiting dialog and notify the error.
            dialog.hide();
            showAndLogErrorMessage('Stored Service VM could not be opened for modification.', status, err);
      }
    });
    
    return false;
}

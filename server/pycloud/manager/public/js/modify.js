
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
    if(!validateMandatoryField(svm_info.serviceId, "Service Id")) return false;
    if(!validateMandatoryField(svm_info.port, "Service Port")) return false;
    if(!validateMandatoryField(svm_info.folder, "VM Image")) return false;
        
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
    if(!validateMandatoryField(svm_info.serviceId, "Service Id", modalDiv)) return false;
    if(!validateMandatoryField(svm_info.port, "Service Port", modalDiv)) return false;
    if(!validateMandatoryField(svm_info.source, "VM Image", modalDiv)) return false;
    
    // Handler to load data when received.
    var successHandler = function(vm_image) {
        // Update Stored SVM fields with new SVM info.
        ssvmFolder = $('#vmStoredFolder');
        ssvmFolder.val(getFileDirectory(vm_image.disk_image));  
        ssvmDiskImagePath = $('#vmDiskImageFile');
        ssvmDiskImagePath.val(vm_image.disk_image);
        ssvmDiskImagePathVal = $('#vmDiskImageFileValue');
        ssvmDiskImagePathVal.val(vm_image.disk_image);                
        ssvmStateImagePath = $('#vmStateImageFile');
        ssvmStateImagePath.val(vm_image.state_image);
        ssvmStateImagePathVal = $('#vmStateImageFileValue');
        ssvmStateImagePathVal.val(vm_image.state_image);                
        
        // Upate the buttons to reflect that we can now modify the SVM.
        $('#new-svm-button').prop('style', 'display:none;');
        $('#modify-svm-button').prop('style', 'display:inline;');    
        
        $('#modal-new-servicevm').modal('hide');  

        // Notify that the process was successful.
        showAndLogSuccessMessage('VM Image was created successfully.');
    };
    
    // Do the post to get data and load the modal.
    ajaxSimplePost(actionURL, jsonData, "Starting and Connecting to Service VM", successHandler, $('#modal-new-servicevm'));       
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start an instance to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function startInstance(url)
{
    // Send additional parameter to ensure we get a full image in the instance, not a linked qcow.
    url = url + "&  clone_full_image=True" ;
    
    // Do the post to get data and load the modal.
    ajaxGet(url, "Starting Instance to Modify SVM", function(response) {
        showAndLogSuccessMessage('Instance was started successfully with id ' + response.SVM_ID + ', VNC open on port ' + response.VNC_PORT);
        $('#svmInstanceId').val(response.SVM_ID);
        $('#modify-svm-button').hide();
        $('#save-svm-button').show();
        $('#discard-svm-button').show();
        $('#vnc-button').show();
    });

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to save an edited SVM.
/////////////////////////////////////////////////////////////////////////////////////
function persistInstance(url)
{
    // Add the instance ID to the URL.
    svmId = $('#svmInstanceId').val();
    url = url + "/" + svmId;

    // Do the post to get data and load the modal.
    ajaxGet(url, "Saving SVM", function(response) {
        showAndLogSuccessMessage('Changes from instance were saved successfully to the permanent VM image.');
        $('#modify-svm-button').show();
        $('#save-svm-button').hide();
        $('#discard-svm-button').hide();
        $('#vnc-button').hide();        
    });

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to discard an edited SVM.
/////////////////////////////////////////////////////////////////////////////////////
function discardInstance(url)
{
    // Add the instance ID to the URL.
    svmId = $('#svmInstanceId').val();
    url = url + "/" + svmId;

    // Do the post to get data and load the modal.
    ajaxGet(url, "Discarding SVM", function(response) {
        showAndLogSuccessMessage('Instance was discarded.');
        $('#modify-svm-button').show();
        $('#save-svm-button').hide();
        $('#discard-svm-button').hide();
        $('#vnc-button').hide();        
    });

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openEditVNC(vncUrl)
{
    // Add the instance ID to the URL.
    svmId = $('#svmInstanceId').val();
    vncUrl = vncUrl + "/" + svmId;
    
    // Handler to load data when received.
    var successHandler = function(response) {
        showAndLogSuccessMessage('VNC window was opened locally on server.');
    };
    
    // Do the post to get data and load the modal.
    ajaxGet(vncUrl, "Starting and Connecting to Service VM", successHandler);    

    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Helper function.
/////////////////////////////////////////////////////////////////////////////////////
function getFileDirectory(filePath) 
{
  if (filePath.indexOf("/") == -1) { // windows
    return filePath.substring(0, filePath.lastIndexOf('\\'));
  } 
  else { // unix
    return filePath.substring(0, filePath.lastIndexOf('/'));
  }
}

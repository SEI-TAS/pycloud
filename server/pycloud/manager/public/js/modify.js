
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

        // Notify that the process was successful.
        showAndLogSuccessMessage('Stored Service VM was created successfully.');
    };
    
    // Do the post to get data and load the modal.
    ajaxSimplePost(actionURL, jsonData, "Starting and Connecting to Service VM", successHandler, $('#modal-new-servicevm'));       
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openEditVNC(vncUrl)
{
    // Add the service ID to the URL.
    serviceId = $('#serviceID').val();
    vncUrl = vncUrl + "/" + serviceId;
    
    // Handler to load data when received.
    var successHandler = function(response) {
        showAndLogSuccessMessage('VM Image was modified successfully.');
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

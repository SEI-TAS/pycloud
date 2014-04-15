
/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to create an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openCreateVNC()
{
    // Show progress bar.
    var dialog = WaitDialog("Starting and Connecting to Service VM");
    dialog.show();
    
    // Get basic information about the form with the new svm.
    var modal = $(this).closest('.modal');
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
        // Notify that the process was successful.
        dialog.hide();
        var alert = Alert('success', 'Stored Service VM was created successfully.');
        alert.show();
        console.log( 'Service VM was created successfully.');        
      },
      error: function( req, status, err ) {
        console.log( 'Something went wrong', status, err );
        dialog.hide();
      }
    });
    
    modal.hide();
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

    // Send the ajax request to start the VNC window.
    $.ajax({
      url: vncUrl,
      dataType: 'json',
      success: function( resp ) {
        // Notify that the process was successful.
        dialog.hide();
        var alert = Alert('success', 'Stored Service VM was modified successfully.');
        alert.show();
        console.log( 'Service VM was modified successfully.');        
      },
      error: function( req, status, err ) {
        console.log( 'Something went wrong', status, err );
        dialog.hide();
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

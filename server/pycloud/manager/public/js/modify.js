
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
        var alert = Alert('success', 'Service VM was modified successfully.');
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

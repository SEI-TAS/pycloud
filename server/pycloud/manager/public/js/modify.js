
/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openEditVNC(vncUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Starting Service VM and opening VNC Window");
    dialog.show();

    // Send the ajax request to start the VNC window.
    $.ajax({
      url: vncUrl,
      dataType: 'json',
      success: function( resp ) {
        // Do nothing, as the VNC window should have opened by now.
        console.log( 'Service VM was modified successfully.');
        dialog.hide();
      },
      error: function( req, status, err ) {
        console.log( 'Something went wrong', status, err );
        dialog.hide();
      }
    });
    
    return false;
}     

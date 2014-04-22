
/////////////////////////////////////////////////////////////////////////////////////
// Function to stop a Service VM through Ajax.
/////////////////////////////////////////////////////////////////////////////////////
function stopSVM(stopUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Stopping Service VM Instance");
    dialog.show();
    
    // Send the ajax request to start the service vm.
    $.ajax({
        url: stopUrl,
        dataType: 'json',
        success: function( resp ) {
            // Parse the response into a JSON structure.
            parsedJsonData = $.parseJSON(JSON.stringify(resp));
                        
            // Check if we got an error.
            if(parsedJsonData.hasOwnProperty('STATUS') && parsedJsonData.STATUS=='NOT OK')
            {
                // Dismiss the waiting dialog and notify the error.
                dialog.hide();
                showAndLogErrorMessage('Service VM Instance could not be stopped.');
            }
            else
            {            
                // Hide the progress bar and reload the page to show the changes.
                dialog.hide();
                window.top.location=window.top.location;
            }
      },
        error: function( req, status, err ) {
            dialog.hide();
            showAndLogErrorMessage('Service VM Instance could not be stopped.', status, err);
      }
    });
}    

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window.
/////////////////////////////////////////////////////////////////////////////////////
function openVNC(vncUrl)
{
    // Send the ajax request to start the VNC window.
    $.ajax({
        url: vncUrl,
        dataType: 'json',
        success: function( resp ) {
            // Do nothing, as the VNC window should have opened by now.
            showAndLogSuccessMessage( 'VNC window opening...');
      },
        error: function( req, status, err ) {
            showAndLogErrorMessage( 'Something went wrong', status, err );
      }
    });
}     


/////////////////////////////////////////////////////////////////////////////////////
// Function to start a Service VM through Ajax, and redirect to the given page.
/////////////////////////////////////////////////////////////////////////////////////
function startSVM(startUrl, redirectUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Starting Service VM Instance");
    dialog.show();
    
    // Send the ajax request to start the service vm.
    $.ajax({
        url: startUrl,
        dataType: 'json',
        success: function( resp ) {
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(resp))
            {
                // Dismiss the waiting dialog and notify the error.
                dialog.hide();
                showAndLogErrorMessage('Service VM Instance could not be started.');
            }
            else
            {      
                // Go to the list of instances.
                dialog.hide();      
                window.location.href = redirectUrl;
            }
        },
        error: function( req, status, err ) {
            showAndLogErrorMessage('Service VM Instance could not be started.', status, err );
        }
    });
} 

/////////////////////////////////////////////////////////////////////////////////////
// Function to confirm to remove a service.
/////////////////////////////////////////////////////////////////////////////////////
function removeServiceConfirmation(removeUrl, serviceId)
{
    // Ask for confirmation.
    BootstrapDialog.confirm('Are you sure you want to delete <strong>'+serviceId+'</strong>?', function(result){
            if(result) {
                removeService(removeUrl, redirectUrl);
            }
        });
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to remove a service.
/////////////////////////////////////////////////////////////////////////////////////
function removeService(removeUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Removing Service");
    dialog.show();
    
    // Send the ajax request to start the service vm.
    $.ajax({
        url: removeUrl,
        dataType: 'json',
        success: function( resp ) {
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(resp))
            {
                // Dismiss the waiting dialog and notify the error.
                dialog.hide();
                showAndLogErrorMessage('There was a problem removing the service.');
            }
            else
            {             
                // Reload page to show changes.
                window.location.href = window.location.href;
            }
        },
        error: function( req, status, err ) {
            dialog.hide();
            showAndLogErrorMessage('There was a problem removing the service.', status, err );
        }
    });
}


/////////////////////////////////////////////////////////////////////////////////////
// Function to start a Service VM through Ajax, and redirect to the given page.
/////////////////////////////////////////////////////////////////////////////////////
function startSVM(startUrl, redirectUrl)
{
    var successHandler = function(response) {
        window.location.href = redirectUrl;
    };
    
    // Do the post to get data and load the modal.
    ajaxGet(startUrl, "Starting Service VM Instance", successHandler);     
} 

/////////////////////////////////////////////////////////////////////////////////////
// Function to confirm to remove a service.
/////////////////////////////////////////////////////////////////////////////////////
function removeServiceConfirmation(removeUrl, serviceId)
{
    // Ask for confirmation.
    BootstrapDialog.confirm('Are you sure you want to delete <strong>'+serviceId+'</strong>?', function(result){
            if(result) {
                removeService(removeUrl);
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

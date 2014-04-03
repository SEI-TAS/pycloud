
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
        window.location.href = redirectUrl;
      },
      error: function( req, status, err ) {
        console.log( 'something went wrong', status, err );
      }
    });
} 

/////////////////////////////////////////////////////////////////////////////////////
// Function to confirm to remove a service.
/////////////////////////////////////////////////////////////////////////////////////
function removeServiceConfirmation(removeUrl, redirectUrl)
{
    // Ask for confirmation.
    objectToDelete = 'test';
    BootstrapDialog.confirm('Are you sure you want to delete <strong>'+objectToDelete+'</strong>?', function(result){
            if(result) {
                removeService(removeUrl, redirectUrl);
            }
        });
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to remove a service.
/////////////////////////////////////////////////////////////////////////////////////
function removeService(removeUrl, redirectUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Removing Service");
    dialog.show();
    
    // Send the ajax request to start the service vm.
    $.ajax({
      url: removeUrl,
      dataType: 'json',
      success: function( resp ) {
        // Reload page to show changes.
        window.location.href = window.location.href;
      },
      error: function( req, status, err ) {
        dialog.hide();
        console.log( 'something went wrong', status, err );
        notify('error', 'There was a problem removing the service.');
      }
    });
}

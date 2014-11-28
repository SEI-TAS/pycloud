/////////////////////////////////////////////////////////////////////////////////////////////////
// Functions used when managing the instance list.
/////////////////////////////////////////////////////////////////////////////////////////////////

function showMigrationModal(migrateUrl)
{
    // Store the migration URL in the modal.
    $('#migrateUrl').val(migrateUrl);

    // Show the modal.
    $('#modal-migrate').modal('show');
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to stop a Service VM through Ajax.
/////////////////////////////////////////////////////////////////////////////////////
function migrateSVM()
{
    var successHandler = function(response) {
        reloadPage();
    };

    // Add the target cloudlet.
    var migrateUrl = $('#migrateUrl').val();
    var targetCloudlet = $('#targetCloudet').val();
    migrateUrl = migrateUrl + '?target=' + targetCloudlet;

    // Do the post to get data and load the modal.
    ajaxGet(migrateUrl, "Migrating Service VM Instance", successHandler);
}
 
/////////////////////////////////////////////////////////////////////////////////////
// Function to stop a Service VM through Ajax.
/////////////////////////////////////////////////////////////////////////////////////
function stopSVM(stopUrl)
{
    var successHandler = function(response) {
        reloadPage();
    };
    
    // Do the post to get data and load the modal.
    ajaxGet(stopUrl, "Stopping Service VM Instance", successHandler);        
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
            if(!ajaxCallWasSuccessful(resp))
            {
               showAndLogErrorMessage('Error opening VNC window'); 
            }
            else
            {
                // Do nothing, as the VNC window should have opened by now.
                showAndLogSuccessMessage( 'VNC window opening...');
            }
      },
        error: function( req, status, err ) {
            showAndLogErrorMessage('Error opening VNC window', status, err );
      }
    });
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {

});

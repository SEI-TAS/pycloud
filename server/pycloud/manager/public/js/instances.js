/////////////////////////////////////////////////////////////////////////////////////////////////
// Functions used when managing the instance list.
/////////////////////////////////////////////////////////////////////////////////////////////////
 
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
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(resp))
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

/////////////////////////////////////////////////////////////////////////////////////
// Function to check if we have to reload the page.
/////////////////////////////////////////////////////////////////////////////////////
function reloadChecker(changesUrl) 
{
    var reloadInterval = 3000; // In milliseconds.
    
    // Send the query to check if there are changes in the list.
    $.ajax({
        url: changesUrl,
        dataType: 'json',            
        success: function (resp) {
            // Parse the response into a JSON structure.
            var jsonData = JSON.stringify(resp);
            var parsedJsonData = $.parseJSON(jsonData);

            // Check if we got a correctly formed JSON.
            if(parsedJsonData.hasOwnProperty('LAST_CHANGE_STAMP'))
            {
                // Check to see if the internal change stamp has been initialized.
                if(typeof(reloadChecker.last_changestamp) === 'undefined') 
                {
                    // It has not... perform the initialization
                    reloadChecker.last_changestamp = parsedJsonData.LAST_CHANGE_STAMP;
                }
                
                // Check if the new timestamp is higher than the last one, which means we have new changes.
                if(parsedJsonData.LAST_CHANGE_STAMP > reloadChecker.last_changestamp)
                {
                    // If there are new changes, reload the window.
                    window.top.location = window.top.location;
                }
            }
            else
            {
                console.log('Error getting last change timestamp.');
            }

            // So that the request ends setTimeout calls a new request.
            setTimeout(function() {reloadChecker(window.changeUrl);}, reloadInterval);
        },
        error: function () {
            // If there is an error in the request the "autoupdate" can continue.
            setTimeout(function() {reloadChecker(window.changeUrl);}, reloadInterval);
        }
    });
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    // Start the load checker, which will check for changes continously.
    console.log('Setting up reload checker:' + window.changeUrl);
    reloadChecker(window.changeUrl);    
});    

/////////////////////////////////////////////////////////////////////////////////////
// Creates a modal dialog to show wait state for a process (no actual progress though).
/////////////////////////////////////////////////////////////////////////////////////
function WaitDialog (headerText) {
    // HTML for the modal dialog.
    var pleaseWaitDiv = '<div class="wait-dialog modal fade" id="pleaseWaitDialog" role="dialog" data-backdrop="static" data-keyboard="false"><div class="modal-dialog" id="pleaseWaitModal"><div class="modal-content"><div class="modal-header"><h3>'+headerText+'...</h3></div><div class="modal-body"><div class="progress progress-striped active"><div class="progress-bar" role="progressbar" style="width: 100%;"></div></div></div></div></div></div>';
    
    // Functions to show and hide the dialog.
    return {
        show: function() {
            // If there were any previous wait dialogs leftovers, remove them.
            $('#pleaseWaitDialog').remove();
            
            // Apend a new wait dialog and show it.
            $('body').append(pleaseWaitDiv);
            $('#pleaseWaitDialog').show();
            $('#pleaseWaitDialog').modal();
        },
        hide: function () {
            var waitDialog = $('#pleaseWaitDialog');
            waitDialog.modal('hide');
        },
    };
}

/////////////////////////////////////////////////////////////////////////////////////
// Creates a notification to inform the user of an event.
/////////////////////////////////////////////////////////////////////////////////////
function Alert(level, message, alertContainer) {
    // Template for the alert message.
    var alertDiv = $('<div id="alert-div" style="position: fixed; top: 55px; display: block; left: 30%; width: 35%;"><div class="alert alert-dismissable fade in alert-'+level+'" id="alert-element"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><div id="alert-text">'+message+'</div></div></div>');

    // Functions.
    return {
        show: function() {
            // Set the container for the alert.
            if(alertContainer == null)
            {
                alertContainer =  $('#navbar-container');
            }
            
            // Show the alert.
           alertContainer.append(alertDiv);
            
            // Add timer to auto-close the alert after some time.
            alertElement = $('#alert-element');
            alertDiv.fadeIn(200, function () {
                setTimeout(function () {
                    alertElement.alert('close');
                    alertElement.parent().remove();
                }, 5000);
            });
        },
    };
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to show a notification and log it in the console.
/////////////////////////////////////////////////////////////////////////////////////
function showAndLogSuccessMessage(message, parent)
{
    // Default value.
    if(typeof(parent)==='undefined') parent = null;
    
    // Log and show alert.
    window.console && console.log(message);
    var alertBox = Alert('success', message, parent);
    alertBox.show();
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to show a notification and log it in the console.
/////////////////////////////////////////////////////////////////////////////////////
function showAndLogErrorMessage(message, status, errorThrown, parent)
{
    // Default values.
    if(typeof(status)==='undefined') status = '';
    if(typeof(errorThrown)==='undefined') errorThrown = '';
    if(typeof(parent)==='undefined') parent = null;
        
    // Log and show alert.
    var fullMsg = message;
    if(errorThrown != '')
        fullMsg = message + ": " + errorThrown;
    window.console && console.log(message, status, errorThrown);
    var alertBox = Alert('danger', fullMsg, parent);
    alertBox.show();
}

/////////////////////////////////////////////////////////////////////////////////////
// If passed a json object, just returns it; if it is a string, it jsonieses it.
/////////////////////////////////////////////////////////////////////////////////////
function getAsJson(response)
{
    // Parse the response into a JSON structure if needed.
    //console.log(response);
    var parsedJsonData = response;
    if(typeof(parsedJsonData)==='string')
        parsedJsonData = $.parseJSON(response);    
    console.log(parsedJsonData);
    return parsedJsonData;    
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to check if an Ajax call was successful.
/////////////////////////////////////////////////////////////////////////////////////
function ajaxCallWasSuccessful(jsonObject)
{    
    // Check if we got an error.
    if(jsonObject.hasOwnProperty('STATUS') && jsonObject.STATUS=='NOT OK')
        return false;
    else
        return true;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to correctly reload a page.
/////////////////////////////////////////////////////////////////////////////////////
function reloadPage()
{
    //window.location.href = window.location.href;
    window.location.reload();
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to post json data through AJAX and reload after the response.
/////////////////////////////////////////////////////////////////////////////////////
function ajaxSimplePost(postURL, dataDict, waitDialogText, onSuccess, modal)
{
    var fileId = null;
    ajaxCall('POST', postURL, dataDict, waitDialogText, onSuccess, fileId, modal);
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to post json data through AJAX and reload after the response, with a file.
/////////////////////////////////////////////////////////////////////////////////////
function ajaxFilePost(postURL, dataDict, waitDialogText, onSuccess, fileId, modal)
{
    ajaxCall('POST', postURL, dataDict, waitDialogText, onSuccess, fileId, modal);
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to send json request through AJAX and reload after the response, with a file.
/////////////////////////////////////////////////////////////////////////////////////
function ajaxGet(getURL, waitDialogText, onSuccess, fileId, modal)
{
    var fileId = null;    
    ajaxCall('GET', getURL, {}, waitDialogText, onSuccess, fileId, modal);
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to post json data through AJAX and reload after the response.
/////////////////////////////////////////////////////////////////////////////////////
function ajaxCall(action, postURL, dataDict, waitDialogText, onSuccess, fileId, modal)
{
    // Check if we got a modal.
    if(typeof(modal)==='undefined') modal = null;
    
    // Show progress bar.
    var dialog = null;
    var description = '';
    if(waitDialogText && typeof(waitDialogText) != 'undefined') {
        dialog = WaitDialog(waitDialogText);
        dialog.show();
        description = waitDialogText.toLowerCase();
    }
    
    // Define our success handler.
    var successHandler = function (response) {
            // Ensure we have a json response.
            var jsonObject = getAsJson(response);
        
            // Check if we got an error.
            if(!ajaxCallWasSuccessful(jsonObject))
            {
                // Dismiss the waiting dialog and notify the error.
                if(dialog) {
                    dialog.hide();
                    showAndLogErrorMessage('There was a problem ' + description + ': ' + jsonObject.error, '', '', modal);
                }
                else {
                    console.log('There was an error getting the result.');
                }
            }
            else
            {             
                // Dismiss dialog and do what we defined for success.
                if(dialog) dialog.hide();
                onSuccess(jsonObject);
            }        
    };
    
    // Check if we have a file or not, to see what post function to use.
    if(fileId === null)
    {
        // Send a regular ajax request.
        $.ajax({
            url: postURL,
            method: action,
            data: dataDict,
            success: function( resp ) {
                successHandler(resp);
            },
            error: function( req, status, err ) {
                if(dialog) {
                    dialog.hide();
                    showAndLogErrorMessage('There was a problem ' + description + '.', status, err, modal);
                }
                else {
                    console.log('There was an error getting the result.');
                }
            }
        });
    }
    else
    {
        // Prepare the ajax request to upload the data.
        $('#' + fileId).ajaxfileupload({
            'action': postURL,
            'params': dataDict,
            'valid_extensions': ['apk'],
            'onComplete': function(resp) {
                console.log('Uploading finished.');
                successHandler(resp);
            }
        });
        
        // Actually trigger the ajax call with upload.
        $('#' + fileId).change();          
    }
}

/////////////////////////////////////////////////////////////////////////////////////
// Generic function to validate mandatory fields.
/////////////////////////////////////////////////////////////////////////////////////
function validateMandatoryField(fieldValue, fieldName, modal)
{
    // Validate that we have all the necessary info.
    var errorHeader = 'You must enter a value for the ';
    //console.log('<' + fieldValue + ">");
    if(typeof(fieldValue) === 'undefined' || fieldValue == null || fieldValue === '')
    {
        // If an input is missing, notify the user and stop the process.        
        var errorMsg = errorHeader + ' ' + fieldName.toLowerCase() + '.';
        showAndLogErrorMessage(errorMsg, "", "", modal);
        return false;
    }
    
    return true;
}

    //////////////////////////////////////////////////////////////////////////////
    // Code to be executed every time a document is loaded.
    //////////////////////////////////////////////////////////////////////////////
    $(document).ready(function () {
        // Extended disable function.
        $.fn.extend({
            disable: function(state) {
                return this.each(function() {
                    var $this = $(this);
                    if($this.is('input, button'))
                      this.disabled = state;
                    else
                      $this.toggleClass('disabled', state);
                });
            }
        });

        // Ensure that disabled link buttons are not clickable.
        $('body').on('click', 'a.disabled', function(event) {
            event.preventDefault();
        });
    });

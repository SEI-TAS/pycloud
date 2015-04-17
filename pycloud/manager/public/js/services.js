/*
KVM-based Discoverable Cloudlet (KD-Cloudlet) 
Copyright (c) 2015 Carnegie Mellon University.
All Rights Reserved.

THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.

Released under a modified BSD license, please see license.txt for full terms.
DM-0002138

KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
MiniMongo
Copyright (c) 2010-2014, Steve Lacy 
All rights reserved. Released under BSD license.
https://github.com/MiniMongo/minimongo/blob/master/LICENSE

Bootstrap
Copyright (c) 2011-2015 Twitter, Inc.
Released under the MIT License
https://github.com/twbs/bootstrap/blob/master/LICENSE

jQuery JavaScript Library v1.11.0
http://jquery.com/
Includes Sizzle.js
http://sizzlejs.com/
Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
Released under the MIT license
http://jquery.org/license
*/

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
                window.location.reload();
            }
        },
        error: function( req, status, err ) {
            dialog.hide();
            showAndLogErrorMessage('There was a problem removing the service.', status, err );
        }
    });
}

function export_svm(url)
{
    var dialog = WaitDialog("Exporting Service");
    dialog.show();

    $.ajax({
       url: url,
       dataType: 'json',
        success: function(resp) {
            dialog.hide();
            if (!ajaxCallWasSuccessful(resp))
            {
                showAndLogErrorMessage('There was a problem exporting the service.');
            }
            else
            {
                Alert("success", "The service has been exported to: " + resp);
            }
        },
        error: function (req, status, err) {
            dialog.hide();
            showAndLogErrorMessage('There was a problem exporting the service.', status, err );
        }
    });
}

function import_svm(url, file_path)
{
    var dialog = WaitDialog("Importing Service");
    dialog.show();

    $.ajax({
        url: url + "?filename=" + file_path,
        dataType: 'json',
        success: function(resp) {
            dialog.hide();
            if (resp.hasOwnProperty('error'))
            {
                alert("Error insert service: " + resp.error);
                showAndLogErrorMessage('There was a problem importing the service: ' + resp.error);
            }
            else
            {
                // Reload page to show changes.
                window.location.reload();
            }
        },
        error: function (req, status, err) {
            dialog.hide();
            showAndLogErrorMessage('There was a problem importing the service.', status, err );
        }
    });
}
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
/////////////////////////////////////////////////////////////////////////////////////////////////
// Functions used when managing the instance list.
/////////////////////////////////////////////////////////////////////////////////////////////////

function showMigrationModal(availableCloudeletsUrl, migrateUrl)
{
    // Store the migration URL in the modal.
    $('#migrateUrl').val(migrateUrl);

    // Get the list of currently available cloudlets through ajax.
    var successHandler = function(availableCloudlets) {
        // Add the cloudelts we found to the list.
        var migrateForm = $('#migrate-svm-form');
        var cloudletsSelect = migrateForm.find('#targetCloudlet');
        cloudletsSelect.empty();
        $.each(availableCloudlets, function(value, key) {
            cloudletsSelect.append($('<option></option>').attr('value', value).text(key));
        });
    };

    // Do the post to get data and load the modal.
    ajaxGet(availableCloudeletsUrl, "Finding cloudlets...", successHandler, $('#modal-migrate'));

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
    var targetCloudlet = $('#targetCloudlet').val();
    migrateUrl = migrateUrl + '?target=' + targetCloudlet;

    // Do the post to get data and load the modal.
    ajaxGet(migrateUrl, "Migrating Service VM Instance", successHandler, $('#modal-migrate'));
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
//
/////////////////////////////////////////////////////////////////////////////////////
function showWifiNetworksModal(availableNetworksUrl)
{
    // Get the list of currently available cloudlets through ajax.
    var successHandler = function(availableNetworks) {
        // Add the networks we found to the list.
        var wifiForm = $('#wifi-connection-form');
        var networksSelect = wifiForm.find('#ssid');
        networksSelect.empty();
        $.each(availableNetworks, function(ssid, isConnected) {
            if(isConnected)
                $("#currentNetwork").text(ssid);
            else
                networksSelect.append($('<option></option>').attr('value', ssid).text(ssid));
        });
    };

    // Do the post to get data and load the modal.
    ajaxGet(availableNetworksUrl, "Finding networks...", successHandler, $('#modal-wifi-connect'));

    $('#modal-wifi-connect').modal('show');
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to connect to a Wifi network through Ajax.
/////////////////////////////////////////////////////////////////////////////////////
function wifiConnection()
{
    var successHandler = function(response) {
        reloadPage();
    };

    // Add the target cloudlet.
    var wifiConnectURL = $('#wifi_url').val();
    var targetSSID = $('#ssid').val();
    var fullURL = wifiConnectURL + '?target=' + targetSSID;

    // Do the post to get data and load the modal.
    ajaxGet(fullURL, "Connecting to Wi-FI Network", successHandler, $('#modal-wifi-connect'));
}


/////////////////////////////////////////////////////////////////////////////////////
// Function to disconnect from a Wifi network through Ajax.
/////////////////////////////////////////////////////////////////////////////////////
function disconnectFromWifiNetwork()
{
    var successHandler = function(response) {
        reloadPage();
    };

    // Do the post to get data and load the modal.
    var fullURL = $("#disconnectButton").attr("href");
    console.log(fullURL);
    ajaxGet(fullURL, "Disconnecting from Wi-FI Network", successHandler, $('#modal-wifi-connect'));
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    $("#disconnectButton").click(function (event) {
        event.preventDefault();
        disconnectFromWifiNetwork();
    })
});

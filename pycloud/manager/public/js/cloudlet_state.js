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
// Functions used to handle cloudlet state.
/////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////
// Function to update status info.
/////////////////////////////////////////////////////////////////////////////////////
function reloadCloudletServerState()
{
    var statusUrl = $("#state_url").val();
    ajaxGet(statusUrl, null, function(response) {
        // Check if we got a correctly formed JSON.
        if(response.hasOwnProperty('cpu_info'))
        {
            $('#cpu_load').text(response.cpu_info.usage);
            $('#cpu_cores').text(response.cpu_info.max_cores);

            var free_memory = parseFloat(response.memory_info.free_memory) / (1024.0 * 1024.0 * 1024.0);
            var max_memory = parseFloat(response.memory_info.max_memory) / (1024.0 * 1024.0 * 1024.0);
            var used_memory = max_memory - free_memory;
            var mem_load = parseFloat(used_memory)/parseFloat(max_memory) * 100.0;
            $('#mem_load').text(mem_load.toFixed(2));
            $('#mem_used').text(used_memory.toFixed(2));
            $('#mem_max').text(max_memory.toFixed(2));
        }
        else
        {
            console.log('Error getting cloudlet status. Got: ' + JSON.stringify(response));
        }
    }, null, false);
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    // Start the load checker, which will check for changes continuously.
    console.log('Setting up reload state.');
    startRecurringTimer(reloadCloudletServerState);
});    

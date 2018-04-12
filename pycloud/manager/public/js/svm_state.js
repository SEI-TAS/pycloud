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
function updateSVMList()
{
    var listUrl = $("#svm_url").val();
    ajaxGet(listUrl, null, function(new_svm_list) {
        // Get the list of the current svms we know about.
        var curr_svm_list = {}
        $(".svm_id").each(function(){
            curr_svm_list[$(this).text()] = true;
        });

        // Go over the new list and add any new SVMs to our table.
        for (var i = 0; i < new_svm_list.length; i++) {
            var new_svm = new_svm_list[i];
            if(!curr_svm_list.hasOwnProperty(new_svm['_id'])) {
                // Reload the page so that new SVMs will show up.
                reloadPage();
            }
        }

        // Go over the old list and reload is SVMs were removed.
        var curr_items = Object.keys(curr_svm_list);
        for (var j = 0; j < curr_items.length; j++) {
            var curr_svm_id = curr_items[j];
            var found = false;
            for (var i = 0; i < new_svm_list.length; i++) {
                var new_svm = new_svm_list[i];
                if (new_svm["_id"] == curr_svm_id) {
                    found = true;
                    break;
                }
            }

            if(!found) {
                // Reload the page so that old SVMs will go away.
                reloadPage();
            }
        }
    }, null, false);
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    // Start the load checker, which will check for changes continuously.
    console.log('Setting up SVM monitoring.');
    startRecurringTimer(updateSVMList);
});    

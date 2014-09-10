/////////////////////////////////////////////////////////////////////////////////////////////////
// Functions used to handle cloudlet state.
/////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////
// Function to update status info.
/////////////////////////////////////////////////////////////////////////////////////
function updateList()
{
    var listUrl = $("#svm_url").val();
    ajaxGet(listUrl, waitDialogText=null, function(response) {
        // Get the list of the current svms we know about.
        var curr_svm_list = {}
        $(".c1").each(function(){
            curr_svm_list[$(this).text()] = true;
        });

        // The list we got from the server with all svms.
        var new_svm_list = response.service_vms;

        // Go over the new list and add any new SVMs to our table.
        for (var i = 0; i < new_svm_list.length; i++) {
            var new_svm = new_svm_list[i];
            if(!curr_svm_list.hasOwnProperty(new_svm['_id'])) {
                // Reload the page so that new SVMs will show up.
                reloadPage();
            }
        }

        // To be called again after the next interval.
        var reloadInterval = 2000; // In milliseconds.
        setTimeout(updateList, reloadInterval);
    });
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    // Start the load checker, which will check for changes continuously.
    console.log('Setting up SVM monitoring.');
    updateList();
});    

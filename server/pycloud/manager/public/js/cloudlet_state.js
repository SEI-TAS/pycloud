/////////////////////////////////////////////////////////////////////////////////////////////////
// Functions used to handle cloudlet state.
/////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////
// Function to update status info.
/////////////////////////////////////////////////////////////////////////////////////
function reloadState()
{
    var statusUrl = $("#state_url").val();
    ajaxGet(statusUrl, waitDialogText=null, function(response) {
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

        // To be called again after the next interval.
        var reloadInterval = 2000; // In milliseconds.
        setTimeout(function() {reloadState();}, reloadInterval);
    });
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    // Start the load checker, which will check for changes continuously.
    console.log('Setting up reload state.');
    //reloadState();
});    


/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openCreateVNC(vncUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Starting and Connecting to Service VM");
    dialog.show();

    // Send the ajax request to start the VNC window.
    $.ajax({
      url: vncUrl,
      dataType: 'json',
      success: function( resp ) {
        // Notify that the process was successful.
        dialog.hide();
        var alert = Alert('success', 'Stored Service VM was modified successfully.');
        alert.show();
        console.log( 'Service VM was modified successfully.');        
      },
      error: function( req, status, err ) {
        console.log( 'Something went wrong', status, err );
        dialog.hide();
      }
    });
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window to edit an SVM.
/////////////////////////////////////////////////////////////////////////////////////
function openEditVNC(vncUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Starting and Connecting to Service VM");
    dialog.show();

    // Send the ajax request to start the VNC window.
    $.ajax({
      url: vncUrl,
      dataType: 'json',
      success: function( resp ) {
        // Notify that the process was successful.
        dialog.hide();
        var alert = Alert('success', 'Stored Service VM was modified successfully.');
        alert.show();
        console.log( 'Service VM was modified successfully.');        
      },
      error: function( req, status, err ) {
        console.log( 'Something went wrong', status, err );
        dialog.hide();
      }
    });
    
    return false;
}

/////////////////////////////////////////////////////////////////////////////////////
// Function to show a notification of a successful edit.
/////////////////////////////////////////////////////////////////////////////////////
function showEditSuccess()
{
    var alert = Alert('success', 'Service was modified successfully.');
    alert.show();
}

/////////////////////////////////////////////////////////////////////////////////////////////////
// Called when the document is loaded.
/////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready( function () {
    // Set up event handlers.
    console.log('Setting up JS actions for the New Service VM modal.');    
    
    // Setup to ensure the New Quiz modal is ready to be used when showing the modal.
    $('#modal-new-servicevm').on('show', prepareNewQuizModal);
    
    // Set actual JS action that will be executed when the "Create" button is pushed.
    //$('.new-quiz-action').click(createQuiz);        
});   

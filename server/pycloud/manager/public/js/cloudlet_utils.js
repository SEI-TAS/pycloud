/////////////////////////////////////////////////////////////////////////////////////
// Creates a modal dialog to show wait state for a process (no actual progress though).
/////////////////////////////////////////////////////////////////////////////////////
function WaitDialog (headerText) {
    var pleaseWaitDiv = $('<div class="modal fade" id="pleaseWaitDialog" role="dialog" data-backdrop="static" data-keyboard="false"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h2>'+headerText+'...</h2></div><div class="modal-body"><div class="progress progress-striped active"><div class="progress-bar" role="progressbar" style="width: 100%;"></div></div></div></div></div></div>');
    return {
        show: function() {
            pleaseWaitDiv.modal();
        },
        hide: function () {
            pleaseWaitDiv.modal('hide');
        },
    };
}

/////////////////////////////////////////////////////////////////////////////////////
// Creates a notification to inform the user of an event.
/////////////////////////////////////////////////////////////////////////////////////
function notify(level, message) {
    // Level class for the alert.
    var levelClass = '';
    if (level === 'error' || level === 'success') {
        levelClass = 'alert-' + level;
    }

    // Only do this if there is a message.
    if (message) {
        // Start with the alert template.
        var alertContainer = $('[data-type=template-alert]').clone();
        
        // Define the absolute position where it will show up.
        alertContainer.css({
            position: 'fixed',
            top: 55
        });
        
        // Add the corresponding class to the alert depending on the message type.
        var alertElement = alertContainer.find('.alert');
        if (levelClass) {
            alertElement.addClass(levelClass);
        }
        
        // Add a fade in effect.
        alertElement.addClass('fade in');

        // Add the message itself to the notification.
        alertElement.find('[data-type=alert-text]').html(message);
        
        // Add the alert container to the page.
        $('div.container').append(alertContainer);
        
        // Add auto-close to the alert after some time.
        alertContainer.fadeIn(200, function () {
            setTimeout(function () {
                alertElement.alert('close');
            }, 5000);
        });
        
        // Add a function to close the alert.
        alertContainer.on('closed', function () {
            alertContainer.remove();
        });
    }
}


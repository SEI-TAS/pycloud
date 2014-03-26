
// Creates a modal dialog to show wait state for a process (no actual progress though).
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

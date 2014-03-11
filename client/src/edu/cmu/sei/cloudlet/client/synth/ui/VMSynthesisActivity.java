package edu.cmu.sei.cloudlet.client.synth.ui;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Locale;

import org.json.JSONObject;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import edu.cmu.sei.cloudlet.client.CurrentCloudlet;
import edu.cmu.sei.cloudlet.client.CloudletReadyApp;
import edu.cmu.sei.cloudlet.client.R;
import edu.cmu.sei.cloudlet.client.models.ServiceVMInstance;
import edu.cmu.sei.cloudlet.client.net.CloudletCommandException;
import edu.cmu.sei.cloudlet.client.net.ServiceVmCommandSender;
import edu.cmu.sei.cloudlet.client.synth.models.OverlayInfo;
import edu.cmu.sei.cloudlet.client.synth.net.SynthesisCommandSender;
import edu.cmu.sei.cloudlet.client.ui.ConnectionInfoFragment;
import edu.cmu.sei.cloudlet.client.TimeLog;

/**
 * This activity is used to guide the process of uploading and synthesizing a VM from an overlay.
 * 
 * @author ssimanta, secheverria
 * 
 */
public class VMSynthesisActivity extends Activity
{
    // Used for Android log debugging/
    private static final String LOG_TAG = VMSynthesisActivity.class.getName();

    // Intent keys used when starting the VMSythesisActivty class.INTENT_EXTRA_BASE_OVERLAY_FOLDER
    public static final String INTENT_EXTRA_BASE_OVERLAY_FOLDER = "edu.cmu.sei.cloudlet.BASE_OVERLAY_FOLDER";
    public static final String INTENT_EXTRA_USER_SELECTED_OVERLAY_FOLDER = "edu.cmu.sei.cloudlet.USER_SELECTED_OVERLAY_FOLDER"; 
    
    // Options for the GUI menu.
    private static final int MENU_OPTION_UPLOAD_OVERLAY = 1;
    private static final int MENU_OPTION_UPLOAD_OVERLAY_JOIN = 2;
    private static final int MENU_OPTION_UPLOAD_OVERLAY_FORCED = 3;
    private static final int MENU_OPTION_STOP_CLOUDLET_VM = 4;    
    private static final int MENU_OPTION_START_CLOUDLET_READY_APP = 5;

    // Overlay info.
    private TextView overlayNameText;       
    private TextView serviceIdText;    
    private TextView baseVMIdText;       
    private TextView servicePortText;    
    
    // Information about the overlay to be sent.
    protected OverlayInfo m_overlayInfo;

    // Information about the VM instance that the overlay was loaded into (after synthesis). 
    protected ServiceVMInstance m_serviceVMInstanceInfo;

    // Options used to show different options in the menu.
    protected boolean remoteServerVMRunning = false;
    
    // Flag used to define whether we want to force uploading an overlay, even if it is already there.
    protected boolean forceUpload = false;
    
    // Flag used to indicate if we want to run in an isolated VM.
    protected boolean runIsolated = true;
    
    // Progress dialog when synthesizing.
    protected ProgressDialog mProgressDialog = null;

    // GUI to show status messages.
    protected TextView eventLogTextView;
    protected ScrollView eventLogScrollView;
    
    // Holds the text to be shown in the main screen, on the fileInfoTextView.
    private String resultsText = "";
    
    // Lock used to prevent losing WiFi if the transfer is in progress and the screen turns off.
    protected WifiManager.WifiLock wifiLock;

    /////////////////////////////////////////////////////////////////////////////////////////////////
    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        // Base and GUI setup.
        super.onCreate(savedInstanceState);
        setContentView(R.layout.synthesis);  
        
        // Get the text elements.
        overlayNameText = (TextView) findViewById(R.id.overlayName);
        serviceIdText = (TextView) findViewById(R.id.serviceId);
        baseVMIdText = (TextView) findViewById(R.id.baseVMId);
        servicePortText = (TextView) findViewById(R.id.servicePortText);
        
        // Load cloudlet information.
        ConnectionInfoFragment connInfoFragment = (ConnectionInfoFragment) getFragmentManager().findFragmentById(R.id.connInfoPanel);
        connInfoFragment.setCloudletInfo(CurrentCloudlet.name, CurrentCloudlet.ipAddress);                    
        
        // Load information about the actual overlay files we want to send.
        String overlayName = loadOverlayInfo(getIntent().getExtras());
        
        // Show overlay data.
        overlayNameText.setText(overlayName);        
        serviceIdText.setText(m_overlayInfo.getServiceVMInfo().getServiceId());
        baseVMIdText.setText(m_overlayInfo.getBaseVMId());
        servicePortText.setText(Integer.toString(m_overlayInfo.getServiceVMInfo().getPort()));

        // Setup initial status messages about setup in GUI.
        eventLogTextView = (TextView) findViewById(R.id.eventLog);
        eventLogTextView.setMaxLines(500);
        eventLogScrollView = (ScrollView) findViewById(R.id.eventScroller);
        addLogMessage("Ready to communicate with Cloudlet.");        
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Gets information about the overlay from the Intent that started the Activity.
     */        
    protected String loadOverlayInfo(Bundle extras)
    {
        if(extras != null)
        {
            // Load information about the overlay files in the given overlay folder.
            final String baseOverlaysFolderPath = extras.getString(INTENT_EXTRA_BASE_OVERLAY_FOLDER);
            final String overlayFolderName = extras.getString(INTENT_EXTRA_USER_SELECTED_OVERLAY_FOLDER);
            if (overlayFolderName != null)
            {
                String overlayFolderPath = baseOverlaysFolderPath + "/" + overlayFolderName;
                m_overlayInfo = new OverlayInfo(overlayFolderPath);
                return overlayFolderName;
            }
        }
        
        return "";
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Event on the activity lifecycle.
     */
    @Override
    protected void onResume()
    {
        // Gets a lock on the Wi-Fi connection to prevent it from turning off after a while (or when the device goes to sleep).
        WifiManager wifiManager = (WifiManager) getSystemService(Context.WIFI_SERVICE);
        wifiLock = wifiManager.createWifiLock(LOG_TAG);
        wifiLock.acquire();
        
        super.onResume();
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Event on the activity lifecycle.
     */    
    @Override
    protected void onPause()
    {
        super.onPause();

        // Release the WiFi lock if our app is taken out of focus.
        if (wifiLock != null)
        {
            wifiLock.release();
            wifiLock = null;
        }
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Fills in the main menu.
     */       
    @Override
    public boolean onPrepareOptionsMenu(Menu menu)
    {
        super.onPrepareOptionsMenu(menu);
        
        menu.clear();
        
        // Only show the Upload option if it is pertinent.
        if(!remoteServerVMRunning)
        {
            menu.add(0, MENU_OPTION_UPLOAD_OVERLAY, 0, "Upload Overlay").setIcon(R.drawable.cloudlet_synth);
            menu.add(0, MENU_OPTION_UPLOAD_OVERLAY_JOIN, 0, "Upload Overlay (join)").setIcon(R.drawable.cloudlet_synth);
            menu.add(0, MENU_OPTION_UPLOAD_OVERLAY_FORCED, 0, "Upload Overlay (forced)").setIcon(R.drawable.cloudlet_synth);
        }        
        // Only show the Stop option if it is pertinent.
        else
        {
            menu.add(0, MENU_OPTION_STOP_CLOUDLET_VM, 0, "Stop Running VM").setIcon(R.drawable.cloudlet_synth);
        }
        
        menu.add(0, MENU_OPTION_START_CLOUDLET_READY_APP, 0, "Start Cloudlet Ready App").setIcon(R.drawable.facerec_app_small);

        return true;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Called when menu options are selected.
     */      
    @Override
    public boolean onMenuItemSelected(int featureId, MenuItem item)
    {
        switch (item.getItemId())
        {
            // The user wants to Upload an overlay and synthesize it into a VM.
            case MENU_OPTION_UPLOAD_OVERLAY:
            {
                forceUpload = false;
                runIsolated = true;
                startAsyncVMSynthesis();
                break;
            }
            // The user wants to Upload an overlay and synthesize it into a VM.
            case MENU_OPTION_UPLOAD_OVERLAY_JOIN:
            {
                forceUpload = false;
                runIsolated = false;
                startAsyncVMSynthesis();
                break;
            }            
            case MENU_OPTION_UPLOAD_OVERLAY_FORCED:
            {
                forceUpload = true;
                runIsolated = true;
                startAsyncVMSynthesis();
                break;
            }
            // The user wants to start the app associated to this overlay.
            case MENU_OPTION_START_CLOUDLET_READY_APP:
            {
                startCloudletReadyApp();
                break;
            }
            // The user wants to stop the current instance.
            case MENU_OPTION_STOP_CLOUDLET_VM:
            {
                // Setup the progress indicator.
                setupProgressDialog();
                
                // Start the async task which will stop the VM through the network on a separate thread.
                CloudletCommAsyncTask stopTask = new CloudletCommAsyncTask(CloudletAction.VM_STOP);
                stopTask.execute();
                break;
            }
        }
        
        return true;
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Shows up a progress message window.
     */        
    private void setupProgressDialog()
    {
        // Setup the progress indicator.
        mProgressDialog = new ProgressDialog(this);
        mProgressDialog.setTitle("Communicating with Cloudlet");
        mProgressDialog.setIndeterminate(false);
        mProgressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);        
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Starts the thread to do VM Synthesis.
     */       
    private void startAsyncVMSynthesis()
    {
        if(CurrentCloudlet.isValid() && m_overlayInfo != null)
        {
            // Setup the progress indicator.
            setupProgressDialog();
            
            // Start the async task which will upload the overlay and ask for its synthesis through the network on a separate thread.
            CloudletCommAsyncTask uploadTask = new CloudletCommAsyncTask(CloudletAction.VM_SYNTH);
            uploadTask.execute();
        }
        else
        {
            Toast.makeText(this, "No cloudlet or overlay info found.", Toast.LENGTH_LONG).show();                    
        }        
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends an intent to start a new app which will connect to a remote Server VM.
     */       
    private void startCloudletReadyApp()
    {
        // Check if we have information about a server running on a VM on the cloudlet.
        boolean serviceVMInstanceInfoIsAvailable = m_serviceVMInstanceInfo != null;
        if (!serviceVMInstanceInfoIsAvailable)
        {
            Toast.makeText(
                    this,
                    "No valid running VM info found. You need to upload the overlay first. ",
                    Toast.LENGTH_LONG).show();
            
            return;
        }

        // Get the intent that should be used for an app associated to this service.
        String serviceId = m_overlayInfo.getServiceVMInfo().getServiceId();

        // Start the cloudlet ready app.
        CloudletReadyApp app = new CloudletReadyApp(serviceId, m_serviceVMInstanceInfo);
        app.start(this);
    }
    
    /**
     * Adds a message to the visual log of events.
     * @param message
     */
    private void addLogMessage(String message)
    {
        // Get a timestamp and add a log message.
        String currentDateTimeString = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(new Date());
        resultsText += "\n" + "[" + currentDateTimeString + "] " + message + "\n";
        eventLogTextView.setText(resultsText);
        
        // Scroll to the bottom of the view.
        eventLogScrollView.post(new Runnable() {            
            @Override
            public void run() {
                eventLogScrollView.fullScroll(View.FOCUS_DOWN);              
            }
        });
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Cloudlet actions told to the async task that handles communication.
     * @author secheverria
     */
    private enum CloudletAction 
    {
        VM_SYNTH,
        VM_STOP
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Status message types for reporting status of an async task.
     * @author secheverria
     */
    private enum StatusMessageType
    {
        START,
        END_SUCCESS,
        END_FAILURE
    }       
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Async Tasks that actually connects to the server and interacts with the
     * HTTP server to perform all the steps to synthesize the VM and launch it.
     * The best way to implement this would be to have a base CommAsyncTask, and implement
     * various derived classes (at least a Synth and a Stop derivates).
     * */
    private class CloudletCommAsyncTask extends AsyncTask<String, Integer, String>
    {        
        // Used to check the status of the async task that handles VM synthesis.
        private static final String ASYNC_TASK_STATUS_SUCCESS = "success";
        private static final String ASYNC_TASK_STATUS_FAILURE = "failure";

        // Various constants used for specifying the progress of the Async task.
        private static final int TASK_PROGRESS_STATE_UPLOAD_BEGIN = 1;
        private static final int TASK_PROGRESS_STATE_VM_SYNTHESIS_BEGIN = 2;
        private static final int TASK_PROGRESS_STATE_LAUNCH_VM_BEGIN = 3;
        private static final int TASK_PROGRESS_STATE_VM_READY_FOR_REQUESTS = 4;
        
        // Message used to display progress while synthesizing.
        private String synthesisProgressText = "";

        // To store information returned by the Cloudlet, to be shown to the user.
        private String lastReplyInfo = "";        
        
        // To store the last error, to be displayed to the user.
        private String lastErrorMessage = "";
        
        // The particular action to execute.
        private CloudletAction action;
        
        // Status messages to show for each action.
        private HashMap<CloudletAction, HashMap<StatusMessageType, String>> statusMessages;
        
        /////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Constructor.
         * @param action The type of action this task is going to be doing.
         */
        public CloudletCommAsyncTask(CloudletAction action)
        {
            super();            
            this.action = action;
            
            // Setup messages for Synth action.
            HashMap<StatusMessageType, String> synthStatusMessages = new HashMap<StatusMessageType, String>();
            synthStatusMessages.put(StatusMessageType.START, "Setting up Server VM in Cloudlet.");
            synthStatusMessages.put(StatusMessageType.END_SUCCESS, "Server VM is ready for requests.");
            synthStatusMessages.put(StatusMessageType.END_FAILURE, "Problem setting up Server VM. ");
            
            // Setup messages for Stop action.
            HashMap<StatusMessageType, String> stopStatusMessages = new HashMap<StatusMessageType, String>();
            stopStatusMessages.put(StatusMessageType.START, "Sending stop command to Cloudlet.");
            stopStatusMessages.put(StatusMessageType.END_SUCCESS, "Successfully stopped Server VM.");
            stopStatusMessages.put(StatusMessageType.END_FAILURE, "A problem occured stopping the Server VM. ");
            
            // Setup the status messages.
            statusMessages = new HashMap<CloudletAction, HashMap<StatusMessageType, String>>();
            statusMessages.put(CloudletAction.VM_SYNTH, synthStatusMessages);
            statusMessages.put(CloudletAction.VM_STOP, stopStatusMessages);
        }
        
        @Override
        /////////////////////////////////////////////////////////////////////////////////////////////////
        protected void onPreExecute()
        {
            if (mProgressDialog != null)
            {
                mProgressDialog.setMessage(statusMessages.get(action).get(StatusMessageType.START));
                mProgressDialog.setCancelable(false);
                mProgressDialog.show();
            }
        }

        @Override
        /////////////////////////////////////////////////////////////////////////////////////////////////        
        protected String doInBackground(String... inputValues)
        {
            String status = ASYNC_TASK_STATUS_SUCCESS;
            
            // Cleanup state variables.
            lastReplyInfo = "";
            lastErrorMessage = "";            

            // Do the whole process.
            if(CurrentCloudlet.isValid())
            {
                if(this.action == CloudletAction.VM_SYNTH)
                {
                    SynthesisCommandSender sender = new SynthesisCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);                
                    status = synthesizeVm(sender);
                    sender.shutdown();
                }
                else if(this.action == CloudletAction.VM_STOP)
                {
                    ServiceVmCommandSender sender = new SynthesisCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);
                    status = stopVm(sender);
                    sender.shutdown();
                }
            }
            else
            {
                Log.e(LOG_TAG, "Attempted to send commands to cloudlet when no valid cloudlet has been selected.");
            }
            
            return status;
        }
        
        /////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Sends all the commands to the Cloudlet to upload, synthesize and start a Server VM.
         * @param sender the object used to send the commands.
         * @return A string with the status.
         */
        private String synthesizeVm(SynthesisCommandSender sender)
        {
            String status = ASYNC_TASK_STATUS_SUCCESS;
            
            try
            {
                // The ID of the VM we want to connect to.
                String serviceId = m_overlayInfo.getServiceVMInfo().getServiceId();
                
                // Create a reusable progress update Integer array.
                Integer[] progressUpdate = new Integer[1];
                
                // Step 1 - Check if the VM is already in the cloudlet, to avoid re-uploading it.
                TimeLog.reset();
                TimeLog.stamp("Segment size: " + sender.FILE_SEGMENT_SIZE + " bytes (" + (sender.FILE_SEGMENT_SIZE/1024/1024) + " MB).");
                TimeLog.stamp("Finding if VM is cached.");
                boolean vmExists = sender.executeFindVm(serviceId);
                TimeLog.stamp("Returned from VM cache request.");
                Log.d(LOG_TAG, "Was Server VM found in cloudlet? " + vmExists);
                Log.d(LOG_TAG, "Force upload? " + forceUpload);

                // Synthesis is only necessary if it is not there... in this case, the overlay is sent and the VM synthesized.
                // Also send if we want to force sending it.
                if(!vmExists || forceUpload)
                {
                    // Check if the Base VM exists in the Cloudlet, to avoid uploading unnecessary files.
                    String baseVMId = m_overlayInfo.getBaseVMId();
                    TimeLog.stamp("Finding if Base VM is in the host.");
                    boolean baseVMExists = sender.executeFindBaseVm(baseVMId);
                    TimeLog.stamp("Returned from Base VM check.");
                    
                    // If it doesn't, stop the synthesis process.
                    if(!baseVMExists)
                    {
                        lastErrorMessage = "Base VM " + baseVMId + " is not available in current Cloudlet.";
                        Log.d(LOG_TAG, lastErrorMessage);
                        status = ASYNC_TASK_STATUS_FAILURE;
                        return status;
                    }
                    
                    // Step 2 - Upload file
                    progressUpdate[0] = TASK_PROGRESS_STATE_UPLOAD_BEGIN;
                    publishProgress(progressUpdate);
                    
                    // Prepare cloudlet for sending an overlay.
                    TimeLog.stamp("Sending overlay files.");
                    sender.executePrepareOverlayUploadRequest();
                    
                    // Send each of the three files of the overlay.
                    sender.executeSendFileInSegments(m_overlayInfo.getImageFilePaths()[0]);
                    sender.executeSendFileInSegments(m_overlayInfo.getImageFilePaths()[1]);
                    sender.executeSendFileInSegments(m_overlayInfo.getMetadataFilePath());
                    
                    TimeLog.stamp("Overlay files sent.");
                    
                    // Step 3 - VM Synthesis
                    progressUpdate[0] = TASK_PROGRESS_STATE_VM_SYNTHESIS_BEGIN;
                    publishProgress(progressUpdate);                
                    
                    // Synthesize the VM.
                    TimeLog.stamp("Requesting VM synthesis.");
                    sender.executeSynthVMRequest();
                    TimeLog.stamp("VM synthesis finished.");
                }
                else
                {
                    Log.d(LOG_TAG, "Overlay not sent to cloudlet since VM is already there.");
                }

                // Step 4 - Launch VM
                progressUpdate[0] = TASK_PROGRESS_STATE_LAUNCH_VM_BEGIN;
                publishProgress(progressUpdate);
                
                // Start it and get its instance information.
                TimeLog.stamp("Requesting VM start.");
                JSONObject jsonResponse = sender.executeStartVMRequest(serviceId, runIsolated);
                TimeLog.stamp("Returned started VM information");
                m_serviceVMInstanceInfo = new ServiceVMInstance(jsonResponse);
                lastReplyInfo = " VM with instance ID " + m_serviceVMInstanceInfo.getInstanceId() + 
                                " available on IP " + m_serviceVMInstanceInfo.getIpAddress() + 
                                " and port " + m_serviceVMInstanceInfo.getPort() + ".";
                Log.d(LOG_TAG, lastReplyInfo);
                remoteServerVMRunning = true;
                
                TimeLog.writeToFile("synthlog.txt");
            }
            catch(CloudletCommandException exception)
            {
                lastErrorMessage = exception.getMessage();
                Log.d(LOG_TAG, lastErrorMessage);
                status = ASYNC_TASK_STATUS_FAILURE;
            }
            catch (IOException e)
            {
                lastErrorMessage = e.getMessage();
                Log.d(LOG_TAG, lastErrorMessage);                
                status = ASYNC_TASK_STATUS_FAILURE;
            }
            
            return status;
        }
        
        /////////////////////////////////////////////////////////////////////////////////////////////////
        /**
         * Sends the commands to the Cloudlet to stop an instance of a Server VM.
         * @param sender the object used to send the commands.
         * @return A string with the status.
         */
        private String stopVm(ServiceVmCommandSender sender)
        {
            String status = ASYNC_TASK_STATUS_SUCCESS;
            
            try
            {
                // Check if there is nothing to stop.
                if(m_serviceVMInstanceInfo == null)
                {
                    lastErrorMessage = "No Server VM instance to stop.";
                    Log.d(LOG_TAG, lastErrorMessage);
                    status = ASYNC_TASK_STATUS_FAILURE;
                }
                else
                {                
                    // Get the ID of the particular instance we already started.
                    String instanceId = m_serviceVMInstanceInfo.getInstanceId();
                    sender.executeStopVMRequest(instanceId);
                    m_serviceVMInstanceInfo = null;
                    remoteServerVMRunning = false;
                }
            }
            catch(CloudletCommandException exception)
            {
                lastErrorMessage = exception.getMessage();
                Log.d(LOG_TAG, lastErrorMessage);
                status = ASYNC_TASK_STATUS_FAILURE;
            }
            
            return status;
        }        

        @Override
        /////////////////////////////////////////////////////////////////////////////////////////////////        
        protected void onPostExecute(String result)
        {
            if (mProgressDialog != null)
            {
                mProgressDialog.dismiss();
            }
            
            // Create a corresponding useful message depending on the success.
            String message = "";
            if (result != null && ASYNC_TASK_STATUS_SUCCESS.equals(result))
            {
                message = statusMessages.get(action).get(StatusMessageType.END_SUCCESS) + lastReplyInfo;
            }
            else
            {
                message = statusMessages.get(action).get(StatusMessageType.END_FAILURE) + lastErrorMessage;
            }
            
            // Show the message in the log.
            addLogMessage(message);
            
            invalidateOptionsMenu();
        }

        /////////////////////////////////////////////////////////////////////////////////////////////////        
        @Override
        protected void onProgressUpdate(Integer... values)
        {
            if (values == null || values.length == 0 || mProgressDialog == null)
                return;

            switch (values[0].intValue())
            {
                case TASK_PROGRESS_STATE_UPLOAD_BEGIN:
                {
                    synthesisProgressText = "- Uploading Overlay files ...";
                    break;
                }
                case TASK_PROGRESS_STATE_VM_SYNTHESIS_BEGIN:
                {
                    synthesisProgressText = "- Overlay files upload - COMPLETE \n\n - Synthesizing VM ...";
                    break;
                }
                case TASK_PROGRESS_STATE_LAUNCH_VM_BEGIN:
                {
                    synthesisProgressText = " - Launching VM ...";
                    break;
                }
                case TASK_PROGRESS_STATE_VM_READY_FOR_REQUESTS:
                {
                    synthesisProgressText = " - VM launched - COMPLETE \n\n VM ready to receive requests.";
                    break;
                }
            }
            
            mProgressDialog.setMessage(synthesisProgressText);            
            super.onProgressUpdate(values);
        }
    }

}

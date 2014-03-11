package edu.cmu.sei.cloudlet.client.ondemand.ui;

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
import edu.cmu.sei.cloudlet.client.ondemand.models.ProvisioningModuleInfo;
import edu.cmu.sei.cloudlet.client.ondemand.net.OnDemandCommandSender;
import edu.cmu.sei.cloudlet.client.ui.ConnectionInfoFragment;
import edu.cmu.sei.cloudlet.client.TimeLog;

/**
 * This activity is used to guide the process of uploading and provisioning a VM from an module.
 * 
 * @author secheverria
 * 
 */
public class ODProvisioningActivity extends Activity
{
    // Used for Android log debugging/
    private static final String LOG_TAG = ODProvisioningActivity.class.getName();

    // Intent keys used when starting the VMSythesisActivty.
    public static final String INTENT_EXTRA_BASE_MODULES_FOLDER = "edu.cmu.sei.cloudlet.BASE_MODULES_FOLDER";
    public static final String INTENT_EXTRA_USER_SELECTED_MODULE_FOLDER = "edu.cmu.sei.cloudlet.USER_SELECTED_MODULE_FOLDER"; 
    
    // Options for the GUI menu.
    private static final int MENU_OPTION_UPLOAD_MODULE = 1;
    private static final int MENU_OPTION_UPLOAD_MODULE_JOIN = 2;
    private static final int MENU_OPTION_UPLOAD_MODULE_FORCED = 3;
    private static final int MENU_OPTION_STOP_CLOUDLET_VM = 4;    
    private static final int MENU_OPTION_START_CLOUDLET_READY_APP = 5;

    // Module info.
    private TextView moduleNameText;       
    private TextView serviceIdText;
    private TextView servicePortText;
    private TextView baselineVMOsFamilyText;       
    
    // Information about the module to be sent.
    protected ProvisioningModuleInfo m_moduleInfo = null;

    // Information about the VM instance that the module was loaded into (after provisioning). 
    protected ServiceVMInstance m_serviceVMInstanceInfo;

    // Options used to show different options in the menu.
    protected boolean remoteServerVMRunning = false;
    
    // Flag used to define whether we want to force uploading a module, even if it a ServiceVM is already there.
    protected boolean forceUpload = false;
    
    // Flag used to indicate if we want to run in an isolated VM.
    protected boolean runIsolated = true;
    
    // Progress dialog when provisioning.
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
        setContentView(R.layout.odp);  
        
        // Get the text elements.
        moduleNameText = (TextView) findViewById(R.id.moduleName);
        serviceIdText = (TextView) findViewById(R.id.serviceId);
        baselineVMOsFamilyText = (TextView) findViewById(R.id.osFamily);
        servicePortText = (TextView) findViewById(R.id.servicePortText);
        
        // Load cloudlet information.
        ConnectionInfoFragment connInfoFragment = (ConnectionInfoFragment) getFragmentManager().findFragmentById(R.id.connInfoPanel);
        connInfoFragment.setCloudletInfo(CurrentCloudlet.name, CurrentCloudlet.ipAddress);                    
        
        // Load information about the actual module files we want to send.
        String moduleName = loadModuleInfo(getIntent().getExtras());
        
        // Show module data.
        if(m_moduleInfo != null)
        {
            moduleNameText.setText(moduleName);        
            serviceIdText.setText(m_moduleInfo.getServiceVMInfo().getServiceId());
            baselineVMOsFamilyText.setText(m_moduleInfo.getBaselineVMInfo().getOsFamily());
            servicePortText.setText(Integer.toString(m_moduleInfo.getServiceVMInfo().getPort()));
        }

        // Setup initial status messages about setup in GUI.
        eventLogTextView = (TextView) findViewById(R.id.eventLog);
        eventLogTextView.setMaxLines(500);
        eventLogScrollView = (ScrollView) findViewById(R.id.eventScroller);
        addLogMessage("Ready to communicate with Cloudlet.");        
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Gets information about the module from the Intent that started the Activity.
     */        
    protected String loadModuleInfo(Bundle extras)
    {
        if(extras != null)
        {
            // Load information about the module files in the given folder.
            final String rootModulesFolder = extras.getString(INTENT_EXTRA_BASE_MODULES_FOLDER);
            final String selectedModuleFolder = extras.getString(INTENT_EXTRA_USER_SELECTED_MODULE_FOLDER);
            if (selectedModuleFolder != null)
            {
                String selectedModulePath = rootModulesFolder + "/" + selectedModuleFolder;
                m_moduleInfo = new ProvisioningModuleInfo(selectedModulePath);
                return selectedModuleFolder;
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
            menu.add(0, MENU_OPTION_UPLOAD_MODULE, 0, "Upload Module").setIcon(R.drawable.cloudlet_synth);
            menu.add(0, MENU_OPTION_UPLOAD_MODULE_JOIN, 0, "Upload Module (join)").setIcon(R.drawable.cloudlet_synth);
            menu.add(0, MENU_OPTION_UPLOAD_MODULE_FORCED, 0, "Upload Module (forced)").setIcon(R.drawable.cloudlet_synth);
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
            // The user wants to Upload an module and provision a VM.
            case MENU_OPTION_UPLOAD_MODULE:
            {
                forceUpload = false;
                runIsolated = true;
                startOnDemandProvisioning();
                break;
            }
            // The user wants to Upload an module and provision a VM, or find a running Service VM to join.
            case MENU_OPTION_UPLOAD_MODULE_JOIN:
            {
                forceUpload = false;
                runIsolated = false;
                startOnDemandProvisioning();
                break;
            }            
            case MENU_OPTION_UPLOAD_MODULE_FORCED:
            {
                forceUpload = true;
                runIsolated = true;
                startOnDemandProvisioning();
                break;
            }
            // The user wants to start the app associated to this module.
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
     * Starts the thread to do On Demand Provisioning
     */       
    private void startOnDemandProvisioning()
    {
        if(CurrentCloudlet.isValid() && m_moduleInfo != null)
        {
            // Setup the progress indicator.
            setupProgressDialog();
            
            // Start the async task which will upload the module and ask for its provisioning through the network on a separate thread.
            CloudletCommAsyncTask uploadTask = new CloudletCommAsyncTask(CloudletAction.VM_PROVISIONING);
            uploadTask.execute();
        }
        else
        {
            Toast.makeText(this, "Cloudlet or module info not found.", Toast.LENGTH_LONG).show();                    
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
                    "No valid running VM info found. You need to upload the module first. ",
                    Toast.LENGTH_LONG).show();
            
            return;
        }

        // Get the intent that should be used for an app associated to this service.
        String serviceId = m_moduleInfo.getServiceVMInfo().getServiceId();

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
        VM_PROVISIONING,
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
     * HTTP server to perform all the steps to provision the VM and launch it.
     * NOTE: A better way to implement this would be to have a base CommAsyncTask, and implement
     * various derived classes (at least a Provision and a Stop derivates).
     * */
    private class CloudletCommAsyncTask extends AsyncTask<String, Integer, String>
    {        
        // Used to check the status of the async task that handles VM provisioning.
        private static final String ASYNC_TASK_STATUS_SUCCESS = "success";
        private static final String ASYNC_TASK_STATUS_FAILURE = "failure";

        // Various constants used for specifying the progress of the Async task.
        private static final int TASK_PROGRESS_STATE_UPLOAD_BEGIN = 1;
        private static final int TASK_PROGRESS_STATE_VM_PROVISIONING_BEGIN = 2;
        private static final int TASK_PROGRESS_STATE_LAUNCH_VM_BEGIN = 3;
        private static final int TASK_PROGRESS_STATE_VM_READY_FOR_REQUESTS = 4;
        
        // Message used to display progress while provisioning.
        private String progressText = "";

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
            
            // Setup messages for Provisioning action.
            HashMap<StatusMessageType, String> provisioningStatusMessages = new HashMap<StatusMessageType, String>();
            provisioningStatusMessages.put(StatusMessageType.START, "Setting up Server VM in Cloudlet.");
            provisioningStatusMessages.put(StatusMessageType.END_SUCCESS, "Server VM is ready for requests.");
            provisioningStatusMessages.put(StatusMessageType.END_FAILURE, "Problem setting up Server VM. ");
            
            // Setup messages for Stop action.
            HashMap<StatusMessageType, String> stopStatusMessages = new HashMap<StatusMessageType, String>();
            stopStatusMessages.put(StatusMessageType.START, "Sending stop command to Cloudlet.");
            stopStatusMessages.put(StatusMessageType.END_SUCCESS, "Successfully stopped Server VM.");
            stopStatusMessages.put(StatusMessageType.END_FAILURE, "A problem occured stopping the Server VM. ");
            
            // Setup the status messages.
            statusMessages = new HashMap<CloudletAction, HashMap<StatusMessageType, String>>();
            statusMessages.put(CloudletAction.VM_PROVISIONING, provisioningStatusMessages);
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
                if(this.action == CloudletAction.VM_PROVISIONING)
                {
                    OnDemandCommandSender sender = new OnDemandCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);                
                    status = provisionVM(sender);
                    sender.shutdown();
                }
                else if(this.action == CloudletAction.VM_STOP)
                {
                    OnDemandCommandSender sender = new OnDemandCommandSender(CurrentCloudlet.ipAddress, CurrentCloudlet.port);
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
         * Sends all the commands to the Cloudlet to upload, provision and start a Server VM.
         * @param sender the object used to send the commands.
         * @return A string with the status.
         */
        private String provisionVM(OnDemandCommandSender sender)
        {
            String status = ASYNC_TASK_STATUS_SUCCESS;
            
            try
            {
                // The ID of the VM we want to connect to.
                String serviceId = m_moduleInfo.getServiceVMInfo().getServiceId();
                
                // Create a reusable progress update Integer array.
                Integer[] progressUpdate = new Integer[1];
                
                // Step 1 - Check if the VM is already in the cloudlet, to avoid re-uploading it.
                TimeLog.reset();
                TimeLog.stamp("Finding if VM is cached.");
                boolean vmExists = sender.executeFindVm(serviceId);
                TimeLog.stamp("Returned from VM cache request.");
                Log.d(LOG_TAG, "Was Server VM found in cloudlet? " + vmExists);
                Log.d(LOG_TAG, "Force upload? " + forceUpload);

                // Provisioning is only necessary if it is not there... in this case, the module is sent and the VM provisioned.
                // Also send if we want to force sending it.
                if(!vmExists || forceUpload)
                {
                    // Step 1
                    // Check if there is a Baseline VM exists in the Cloudlet, that matches the Baseline VM metadata.
                    TimeLog.stamp("Finding if there is a suitable Baseline VM is in the host.");
                    String baselineMetadataFilepath = m_moduleInfo.getBaselineVMMetadataFilePath();
                    String baselineVMId = sender.executeFindBaselineVm(baselineMetadataFilepath);
                    TimeLog.stamp("Returned from Baseline VM search.");
                    
                    // If it doesn't, stop the process.
                    if(baselineVMId == null)
                    {
                        lastErrorMessage = "No matching Baseline VM is available in current Cloudlet.";
                        Log.d(LOG_TAG, lastErrorMessage);
                        status = ASYNC_TASK_STATUS_FAILURE;
                        return status;
                    }
                    
                    // Step 2 - Upload file
                    progressUpdate[0] = TASK_PROGRESS_STATE_UPLOAD_BEGIN;
                    publishProgress(progressUpdate);
                    
                    // Send each of the files of the module, and provision the VM.
                    TimeLog.stamp("Sending module files and waiting for provisioning.");
                    sender.executeProvisionRequest(baselineVMId, m_moduleInfo.getManifestFilePath(), m_moduleInfo.getServiceVMMetadataFilePath());
                    TimeLog.stamp("Module files sent, provisioning finshed.");
                }
                else
                {
                    Log.d(LOG_TAG, "Module not sent to cloudlet since Service VM is already there.");
                }

                // Step 3 - Launch VM
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
                
                TimeLog.writeToFile("odplog.txt");
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
                    progressText = "- Uploading module files ...";
                    break;
                }
                case TASK_PROGRESS_STATE_VM_PROVISIONING_BEGIN:
                {
                    progressText = "- Module files upload - COMPLETE \n\n - Provisioning VM ...";
                    break;
                }
                case TASK_PROGRESS_STATE_LAUNCH_VM_BEGIN:
                {
                    progressText = " - Launching VM ...";
                    break;
                }
                case TASK_PROGRESS_STATE_VM_READY_FOR_REQUESTS:
                {
                    progressText = " - VM launched - COMPLETE \n\n VM ready to receive requests.";
                    break;
                }
            }
            
            mProgressDialog.setMessage(progressText);            
            super.onProgressUpdate(values);
        }
    }

}

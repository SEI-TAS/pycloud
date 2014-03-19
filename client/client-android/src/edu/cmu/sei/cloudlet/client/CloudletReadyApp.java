package edu.cmu.sei.cloudlet.client;

import edu.cmu.sei.cloudlet.client.models.ServiceVMInstance;
import edu.cmu.sei.cloudlet.client.synth.ui.VMSynthesisActivity;
import android.app.Activity;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

/**
 * Handles starting cloudlet-ready apps.
 * @author secheverria
 *
 */
public class CloudletReadyApp
{
    // Used for Android log debugging/
    private static final String LOG_TAG = VMSynthesisActivity.class.getName();
    
    // Intent keys used when starting an external cloudlet-ready app.
    public static final String INTENT_ACTION_START_SUFFIX = ".CLOUDLET_READY_START";
    public static final String INTENT_EXTRA_APP_SERVER_IP_ADDRESS = "edu.cmu.sei.cloudlet.appServerIp";
    public static final String INTENT_EXTRA_APP_SERVER_PORT ="edu.cmu.sei.cloudlet.appServerPort";    

    // The action the activity is listening to.
    private String m_intentAction;
    
    // The server information we have to pass to the activity.
    private ServiceVMInstance m_serverInfo;  
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * The constructor.
     * @param intentActionPrefix the prefix for the intent action, usually the app's package.
     * @param serverInfo
     */
    public CloudletReadyApp(String intentActionPrefix, ServiceVMInstance serverInfo)
    {
        m_intentAction = intentActionPrefix + INTENT_ACTION_START_SUFFIX;
        m_serverInfo = serverInfo;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Starts this cloudlet-ready activity.
     * @param parentActivity the activity that is starting this new one.
     */
    public void start(Activity parentActivity)
    {
        // Set up an intent with the server's IP and port for the cloudlet-ready app.
        Intent appIntent = new Intent();
        appIntent.setAction(m_intentAction);
        appIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        appIntent.putExtra(INTENT_EXTRA_APP_SERVER_IP_ADDRESS,
                            m_serverInfo.getIpAddress());
        appIntent.putExtra(INTENT_EXTRA_APP_SERVER_PORT,
                            m_serverInfo.getPort());

        // Start the new cloudlet-ready activity.
        try
        {
            parentActivity.startActivity(appIntent);
        }
        catch (Exception e)
        {
            Log.e(LOG_TAG,
                    "Error starting cloudlet-ready activity: "
                            + e.toString());
            Toast.makeText(parentActivity,
                    "No cloudlet-ready activity could be found.",
                    Toast.LENGTH_LONG).show();
        }
    }
}

package edu.cmu.sei.cloudlet.client;

import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.ServiceVM;
import edu.cmu.sei.cloudlet.client.models.ServiceVMInstance;
import edu.cmu.sei.cloudlet.client.synth.ui.VMSynthesisActivity;
import android.app.Activity;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

/**
 * Handles starting cloudlet-ready apps.
 * @author secheverria
 *
 */
public class CloudletReadyApp
{
    private static XLogger log = XLoggerFactory.getXLogger(CloudletReadyApp.class);

    // Used for Android log debugging/
    private static final String LOG_TAG = VMSynthesisActivity.class.getName();
    
    // Intent keys used when starting an external cloudlet-ready app.
    public static final String INTENT_ACTION_START_SUFFIX = ".CLOUDLET_READY_START";
    public static final String INTENT_EXTRA_APP_SERVER_IP_ADDRESS = "edu.cmu.sei.cloudlet.appServerIp";
    public static final String INTENT_EXTRA_APP_SERVER_PORT ="edu.cmu.sei.cloudlet.appServerPort";    

    // The action the activity is listening to.
    private String m_intentAction;

    private final String addr;
    private final int port;
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * The constructor.
     * @param intentActionPrefix the prefix for the intent action, usually the app's package.
     * @param serverInfo
     */
    public CloudletReadyApp(String intentActionPrefix, ServiceVMInstance serverInfo)
    {
        m_intentAction = intentActionPrefix + INTENT_ACTION_START_SUFFIX;
        addr = serverInfo.getIpAddress();
        port = serverInfo.getPort();
    }

    public CloudletReadyApp(Service service)
    {
        m_intentAction = service.getServiceId() + INTENT_ACTION_START_SUFFIX;
        addr = service.getServiceVM().getAddress().getHostAddress();
        port = service.getServiceVM().getPort();

        log.info("Creating app: " + m_intentAction);
        log.info("Address: " + addr);
        log.info("Port: " + port);
    }

    public CloudletReadyApp(ServiceVM serviceVM)
    {
        m_intentAction = serviceVM.getServiceId() + INTENT_ACTION_START_SUFFIX;
        addr = serviceVM.getAddress().getHostAddress();
        port = serviceVM.getPort();

        log.info("Creating app: " + m_intentAction);
        log.info("Address: " + addr);
        log.info("Port: " + port);
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
        appIntent.putExtra(INTENT_EXTRA_APP_SERVER_IP_ADDRESS, addr);
        appIntent.putExtra(INTENT_EXTRA_APP_SERVER_PORT, port);

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

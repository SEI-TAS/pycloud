package edu.cmu.sei.cloudlet.client.push.net;

import org.json.JSONException;
import org.json.JSONObject;

import edu.cmu.sei.cloudlet.client.net.CloudletCommandException;
import edu.cmu.sei.cloudlet.client.net.ServiceVmCommandSender;

/**
 * Class that handles the protocol to communicate Cloudlet Push commands with a CloudletServer.
 * The protocol supported is that of the Baseline VM Synthesis Prototype.
 * @author secheverria
 *
 */
public class CloudletPushCommandSender extends ServiceVmCommandSender
{
    // Used to identify logging statements.
    private static final String LOG_TAG = CloudletPushCommandSender.class.getName();

    // Commands sent to CloudletServer.
    private static final String HTTP_GET_APPS_LIST = "api/app/getList";
    private static final String HTTP_GET_APP = "api/app/getApp";
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Constructor.
     */    
    public CloudletPushCommandSender(String cloudletIPAddress, int cloudletPort)
    {
        super(cloudletIPAddress, cloudletPort);
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to get a list of existing apps in the server.
     * @returns A structure with a list of available apps.
     */
    public String executeGetAppsList() throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_GET_APPS_LIST;
        
        // Execute the command.
        String response = sendCommand(commandWithParams);
        
        // Just return the string response.
        return response;        
    }
    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to get a particular app.
     * @returns A structure with a list of available apps.
     */
    public String executeGetApp(String appName, String apkFileName) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_GET_APP + "?appName=" + appName;
        
        // Execute the command.
        String response = sendCommand(commandWithParams, null, apkFileName);
        
        return response;
    }        

}

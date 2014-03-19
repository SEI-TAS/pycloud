package edu.cmu.sei.cloudlet.client.models;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * 
 * Class used to store information about an instance of a Service VM running on a cloudlet.
 * 
 * @author secheverria
 * 
 */
public class ServiceVMInstance
{
    public static final String LOG_TAG = ServiceVMInstance.class.getName();

    // Keys to get information from a JSON object.
    public static final String IP_ADDRESS_KEY = "IP_ADDRESS";
    public static final String PORT_KEY = "PORT";
    public static final String INSTANCE_ID_KEY = "INSTANCE_ID";

    // The connection information of the ServiceVM, plus the ID of the instance.
    protected String ipAddress;
    protected int port;
    protected String instanceId;

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Constructor.
     * @param jsonObj A Json object with the data.
     */
    public ServiceVMInstance(final JSONObject jsonObj)
    {
        if (jsonObj != null)
        {
            try
            {
                this.ipAddress = jsonObj.getString(IP_ADDRESS_KEY);
                this.port = jsonObj.getInt(PORT_KEY);
                this.instanceId = jsonObj.getString(INSTANCE_ID_KEY);

            }
            catch (JSONException e)
            {
                e.printStackTrace();
            }
        }
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String getIpAddress()
    {
        return ipAddress;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public int getPort()
    {
        return port;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String getInstanceId()
    {
        return instanceId;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String toString()
    {
        StringBuffer buf = new StringBuffer();
        buf.append("ServiceVMInstanceInfo ->").append("[").append("IP: ")
                .append(ipAddress != null ? ipAddress : "null")
                .append(" , PORT: ").append(port).append("]")
                .append(" , INSTANCE_ID: ").append(instanceId).append("]");        
        return buf.toString();
    }
}

package edu.cmu.sei.cloudlet.client.net;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Class that handles the protocol to communicate ServiceVM commands with a CloudletServer.
 * @author secheverria
 *
 */
public class ServiceVmCommandSender extends CloudletCommandSender
{
    // Used to identify logging statements.
    private static final String LOG_TAG = ServiceVmCommandSender.class.getName();

    // Commands sent to CloudletServer.
    private static final String HTTP_COMMAND_FIND_VM = "api/servicevm/find";
    private static final String HTTP_COMMAND_START_VM = "api/servicevm/start";
    private static final String HTTP_COMMAND_STOP_VM = "api/servicevm/stop";    
    
    // Key used to check response to the existence command.
    private static final String VM_EXISTS_KEY = "VM_EXISTS";

    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Main constructor.
     */
    public ServiceVmCommandSender(String cloudletIPAddress, int cloudletPort)
    {
        super(cloudletIPAddress, cloudletPort);
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to check if a certain Service VM exists in the Cloudlet already.
     * @param serviceId The ID of the service we are trying to check for existence. 
     * @throws CloudletCommandException 
     * @returns True if it exists, false otherwise.
     */
    public boolean executeFindVm(String serviceId) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_FIND_VM + "?serviceId=" + serviceId;
        
        // Execute the command.
        String response = sendCommand(commandWithParams);
        
        // Parse the response into a JSON structure, and return it.
        JSONObject jsonResponse = null;
        try
        {
            jsonResponse = new JSONObject(response);
            String vmExistsText = jsonResponse.getString(VM_EXISTS_KEY);
            if(vmExistsText.equals("True"))
                return true;
            else
                return false;
        }
        catch (JSONException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        return false;
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to start a VM.
     * @param serviceId The ID of the service we are trying to start an instance of.
     * @param runIsolated True if we want to run in our own VM, false if we can join an existing one.
     * @throws CloudletCommandException 
     * @returns A structure with information about the VM that was started.
     */
    public JSONObject executeStartVMRequest(String serviceId, boolean runIsolated) throws CloudletCommandException
    {
        String isolatedParam = "true";
        if(runIsolated == false)
        {
            isolatedParam = "false";
        }
        
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_START_VM + "?serviceId=" + serviceId + "&isolated=" + isolatedParam;
        
        // Execute the command.
        String response = sendCommand(commandWithParams);
        
        // Parse the response into a JSON structure, and return it.
        JSONObject jsonResponse = null;
        try
        {
            jsonResponse = new JSONObject(response);
        }
        catch (JSONException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return jsonResponse;
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to stop a VM.
     * @param instanceId The ID of the instance of a certain Service VM we want to stop. 
     * @throws CloudletCommandException 
     */
    public void executeStopVMRequest(String instanceId) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_STOP_VM + "?instanceId=" + instanceId;
        
        // Execute the command.        
        sendCommand(commandWithParams);
    }
}

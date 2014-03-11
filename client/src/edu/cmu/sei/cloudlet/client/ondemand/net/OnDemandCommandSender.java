package edu.cmu.sei.cloudlet.client.ondemand.net;

import java.io.File;
import java.io.UnsupportedEncodingException;

import org.apache.http.entity.mime.HttpMultipartMode;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.StringBody;
import org.json.JSONException;
import org.json.JSONObject;

import edu.cmu.sei.cloudlet.client.net.CloudletCommandException;
import edu.cmu.sei.cloudlet.client.net.ServiceVmCommandSender;

/**
 * Class that handles the protocol to communicate On-Demand Provisioning commands with a CloudletServer.
 * The protocol supported is that of the Baseline Cloudlet Prototype.
 * @author secheverria
 *
 */
public class OnDemandCommandSender extends ServiceVmCommandSender
{
    // Used to identify logging statements.
    private static final String LOG_TAG = OnDemandCommandSender.class.getName();

    // Commands sent to CloudletServer.
    private static final String HTTP_COMMAND_FIND_BASELINE_VM = "odp/http_find_baseline_vm";
    private static final String HTTP_COMMAND_PROVISION_MODULE = "odp/http_provision_module";

    // Keys used to check response to the existence command.
    private static final String VM_EXISTS_KEY = "VM_EXISTS";
    private static final String MATCHING_VM_ID = "BASELINE_VM_ID";

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Constructor.
     */    
    public OnDemandCommandSender(String cloudletIPAddress, int cloudletPort)
    {
        super(cloudletIPAddress, cloudletPort);
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to check there are Baseline VMs that match the given metadata.
     * @param baselineMetadataFilepath The full path of the metadata file describing the Baseline VM to find. 
     * @throws CloudletCommandException 
     * @returns The BaselineVM id found, or null if no appropriate Baseline VM was available.
     */
    public String executeFindBaselineVm(String baselineMetadataFilepath) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_FIND_BASELINE_VM;
        
        // Create the entity to hold the files, plus the baseline VM id to be used.        
        MultipartEntity multiPartEntity = new MultipartEntity(HttpMultipartMode.BROWSER_COMPATIBLE);
        multiPartEntity.addPart("baselineMetadataFile", new FileBody(new File(baselineMetadataFilepath)));
        
        // Execute the command.
        String response = sendCommand(commandWithParams, multiPartEntity);
        
        // Parse the response into a JSON structure, and return it.
        JSONObject jsonResponse = null;
        try
        {
            jsonResponse = new JSONObject(response);
            String vmExistsText = jsonResponse.getString(VM_EXISTS_KEY);
            String baselineVmId = jsonResponse.getString(MATCHING_VM_ID);
            if(vmExistsText.equals("True"))
                return baselineVmId;
            else
                return null;
        }
        catch (JSONException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        return null;
    }       
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to provision a VM with the module sent to the server.
     * @param baselineVmId The full path of the provisioning script (manifest, module) to send.
     * @param scriptFilePath The full path of the provisioning script (manifest, module) to send.
     * @param svmMetadataFilePath The full path of the ServiceVM metadata file describing the VM to provision.
     * @throws CloudletCommandException 
     */
    public void executeProvisionRequest(String baselineVmId, String scriptFilePath, String svmMetadataFilePath) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_PROVISION_MODULE; 

        // Create the entity to hold the files, plus the baseline VM id to be used.        
        MultipartEntity multiPartEntity = new MultipartEntity(HttpMultipartMode.BROWSER_COMPATIBLE);        
        try
        {
            multiPartEntity.addPart("baselineVmId", new StringBody(baselineVmId));            
            multiPartEntity.addPart("serviceVMMetadatafile", new FileBody(new File(svmMetadataFilePath)));
            multiPartEntity.addPart("moduleFile", new FileBody(new File(scriptFilePath)));            
        }
        catch (UnsupportedEncodingException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        // Execute the command.        
        sendCommand(commandWithParams, multiPartEntity);
    }       
}

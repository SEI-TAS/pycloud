package edu.cmu.sei.cloudlet.client.synth.net;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.UnsupportedEncodingException;

import org.apache.http.entity.mime.HttpMultipartMode;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.entity.mime.content.ByteArrayBody;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.StringBody;
import org.json.JSONException;
import org.json.JSONObject;

import edu.cmu.sei.cloudlet.client.net.CloudletCommandException;
import edu.cmu.sei.cloudlet.client.net.ServiceVmCommandSender;

/**
 * Class that handles the protocol to communicate Synthesis commands with a CloudletServer.
 * The protocol supported is that of the Baseline VM Synthesis Prototype.
 * @author secheverria
 *
 */
public class SynthesisCommandSender extends ServiceVmCommandSender
{
    // Used to identify logging statements.
    private static final String LOG_TAG = SynthesisCommandSender.class.getName();

    // Commands sent to CloudletServer.
    private static final String HTTP_COMMAND_FIND_BASE_VM = "synth/http_find_base_vm";
    private static final String HTTP_COMMAND_PREPARE_OVERLAY_UPLOAD = "synth/http_prepare_overlay_upload";
    private static final String HTTP_COMMAND_START_FILE_UPLOAD = "synth/http_start_file_upload";
    private static final String HTTP_COMMAND_UPLOAD_FILE_SEGMENT = "synth/http_upload_file_segment";
    private static final String HTTP_COMMAND_SYNTH_VM = "synth/http_synth_vm";

    // Key used to check response to the existence command.
    private static final String VM_EXISTS_KEY = "VM_EXISTS";
    
    // Size of each segment of a file to send, when sending a file in segments.
    public static final int FILE_SEGMENT_SIZE = 30*1024*1024;   // 12 MB.

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Constructor.
     */    
    public SynthesisCommandSender(String cloudletIPAddress, int cloudletPort)
    {
        super(cloudletIPAddress, cloudletPort);
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to check if a certain Base VM exists in the Cloudlet already.
     * @param vmId The ID of the Base VM we are trying to check for existence. 
     * @throws CloudletCommandException 
     * @returns True if it exists, false otherwise.
     */
    public boolean executeFindBaseVm(String vmId) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_FIND_BASE_VM + "?vmId=" + vmId;
        
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
     * Sends the command to prepare the upload of an overlay.
     * @throws CloudletCommandException 
     */
    public void executePrepareOverlayUploadRequest() throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_PREPARE_OVERLAY_UPLOAD;
        
        // Execute the command.        
        sendCommand(commandWithParams);
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Sends multiple commands to send a file in segments, to enable streaming processing of it.
     * @param filePath The full path of the file to send.
     * @throws CloudletCommandException 
     */
    public void executeSendFileInSegments(String filePath) throws CloudletCommandException
    {
        // Open the file.
        final File inputFile = new File(filePath);
        String fileName = inputFile.getName();
        FileInputStream fileStream = null;
        try
        {
            fileStream = new FileInputStream(inputFile);
        }
        catch (FileNotFoundException e1)
        {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        
        // Send the file start command.
        long fileSize = inputFile.length();
        executeStartFileUploadRequest(fileName, fileSize);

        // Loop to send each segment.
        for (int i=0; i < inputFile.length(); i += FILE_SEGMENT_SIZE) 
        {
            // We will sent either the segment size, or the remaining bytes if it is the last segment.
            int segmentLength = Math.min(FILE_SEGMENT_SIZE, (int)inputFile.length() - i);                        
            byte[] segmentBytes = null;
            
            // If the segment length is bigger than the actual file, we will send the file as a whole to avoid loading it into a 
            // memory array (which will most likely fail if the file is too big).
            boolean sendCompleteFile = false;
            if(segmentLength >= fileSize)
            {
                sendCompleteFile = true;
            }            
            
            // If we are actually sending segments, then load this segment.
            if(!sendCompleteFile)
            {
                try
                {
                    // Read the next segment.
                    segmentBytes = new byte[segmentLength];
                    fileStream.read(segmentBytes);
                }
                catch(OutOfMemoryError e)
                {
                    throw new CloudletCommandException("Not enough memory to load segment of size " + segmentLength);
                }            
                catch (IOException e) 
                {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
            else
            {
                // If we are sending the full file, we have to pass the full file path.
                fileName = filePath;
            }
            
            // Send the file segment.            
            executeUploadFileSegmentRequest(fileName, segmentBytes, i);
        }
        
        try
        {
            if(fileStream != null)
                fileStream.close();
        }
        catch (IOException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to start a file upload.
     * @param fileName The name of the file to be sent.
     * @param fileLength The length of the file to be sent.  
     * @throws CloudletCommandException 
     */
    private void executeStartFileUploadRequest(String fileName, long fileLength) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_START_FILE_UPLOAD + "?fileName=" + fileName + "&fileLength=" + fileLength;
        
        // Execute the command.        
        sendCommand(commandWithParams);
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to send a new segment of a file.
     * @param fileName The name of the file to be sent, or full path if it is sent as a whole.
     * @param segment The bytes being sent, part of the file, or null if the whole file is being sent.
     * @param startPos The byte (starting from one) of the file being sent where this segment starts.
     * @throws CloudletCommandException 
     */
    private void executeUploadFileSegmentRequest(String fileName, byte[] segment, int startPos) throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_UPLOAD_FILE_SEGMENT; 

        // Calculate the length of the segment or file.
        long segmentLength = 0;
        if(segment != null)
        {
            segmentLength = segment.length;
        }
        else
        {
            segmentLength = new File(fileName).length();
        }

        // Create the entity to hold the file segment, plus description data.        
        MultipartEntity multiPartEntity = new MultipartEntity(HttpMultipartMode.BROWSER_COMPATIBLE);        
        try
        {
            // Load the segment or the whole file, depending on the input.
            if(segment != null)
            {
                multiPartEntity.addPart("newFileSegment", new ByteArrayBody(segment, fileName));
            }
            else
            {
                multiPartEntity.addPart("newFileSegment", new FileBody(new File(fileName)));
            }
            
            // Add details about the size and location in the complete file.
            multiPartEntity.addPart("startByte", new StringBody(String.valueOf(startPos)));
            multiPartEntity.addPart("endByte", new StringBody(String.valueOf(startPos + segmentLength)));
        }
        catch (UnsupportedEncodingException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        // Execute the command.        
        sendCommand(commandWithParams, multiPartEntity);
    }       

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends the command to synthesize the VM for the overlay that is currently in the server.
     * @throws CloudletCommandException 
     */
    public void executeSynthVMRequest() throws CloudletCommandException
    {
        // Add the parameters to the command.
        String commandWithParams = HTTP_COMMAND_SYNTH_VM;
        
        // Execute the command.        
        sendCommand(commandWithParams);
    }    
}

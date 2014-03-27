package edu.cmu.sei.cloudlet.client.net;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;
import java.net.URISyntaxException;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.methods.HttpRequestBase;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;

import android.util.Log;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

/**
 * Class that handles HTTP communication with a CloudletServer.
 * Only provides the common functions for communication, not the protocol itself.
 * Other classes should extend this one to implement the actual protocols.
 * @author secheverria
 *
 */
public class CloudletCommandSender
{
    private static final XLogger log = XLoggerFactory.getXLogger(CloudletCommandSender.class);
    // Used to identify logging statements.
    private static final String LOG_TAG = CloudletCommandSender.class.getName();

    // Connectivity timeouts.
    private static final int CONNECTION_TIMEOUT = 60 * 1000;    // 1 minute.
    private static final int SOCKET_TIMEOUT = 9 * 1000000;      // 2.5 hours.

    // HTTP status codes.
    private static final int HTTP_RESPONSE_OKAY_CODE = 200;
    
    // The HTTP client to use.
    protected DefaultHttpClient m_httpClient;
    
    // The base URI for the server we are communicating with.
    protected String m_cloudletURI = null;

    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Main constructor.
     */
    public CloudletCommandSender(String cloudletIPAddress, int cloudletPort)
    {
        // Setup the root URI we will be using.
        m_cloudletURI = "http://" + cloudletIPAddress + ":" + cloudletPort + "/";
        
        // Prepare the HTTP client to use.
        setUpHttpClient();
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Shutdown the HTTP connnections. 
     */
    public void shutdown()
    {
        if(m_httpClient != null)
        {
            m_httpClient.getConnectionManager().shutdown();
        }
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sets up an HTTP client configured for a connection through this Cloudlet protocol.
     */
    private void setUpHttpClient()
    {
        final HttpParams httpParameters = new BasicHttpParams();

        // Set the timeout in milliseconds until a connection is established.
        HttpConnectionParams.setConnectionTimeout(httpParameters, CONNECTION_TIMEOUT);
        
        // Set the default socket timeout (SO_TIMEOUT) in milliseconds which is the timeout for waiting for data.
        HttpConnectionParams.setSoTimeout(httpParameters, SOCKET_TIMEOUT);     

        // Just create the client.
        m_httpClient = new DefaultHttpClient(httpParameters);
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Wrapper for the sendCommand method, when no multipartdata is required.
     * @param command The command to append to the URI.
     * @return A String with the response received from the server.
     * @throws CloudletCommandException 
     */
    protected String sendCommand(String command) throws CloudletCommandException
    {
        return sendCommand(command, null, "");
    }
    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Wrapper for the sendCommand method, when multipartdata is required but not output file is received.
     * @param command The command to append to the URI.
     * @param multipartData The multipart data to send.
     * @return A String with the response received from the server.
     * @throws CloudletCommandException 
     */
    protected String sendCommand(String command, MultipartEntity multipartData) throws CloudletCommandException
    {
        return sendCommand(command, multipartData, "");
    }    
  
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Sends an HTTP command which requires no processing in its answer.
     * @param command The command to append to the URI.
     * @param multipartData The multipart data to send.
     * @param outputFile The file path to output a file response to, or empty string if there is no file as a return. 
     * @return A String with the response received from the server.
     * @throws CloudletCommandException 
     */
    protected String sendCommand(String command, MultipartEntity multipartData, String outputFile) throws CloudletCommandException
    {
        // First sent the start request message.
        String responseText = "";
        try 
        {
            HttpRequestBase request;
            if (multipartData != null)
                request = new HttpPut();
            else
                request = new HttpGet();
            // Gets the full URI of the command.
            //HttpPut request = new HttpPut();
            URI fullURI = getCommandURI(command);
			Log.d(LOG_TAG, "URI: " + fullURI.toASCIIString());
            Log.d(LOG_TAG, fullURI.getHost());
            request.setURI(fullURI);
            
            // If there is multipart data, add it.
            if(multipartData != null)
            {
                ((HttpPut)request).setEntity(multipartData);
                request.setHeader(multipartData.getContentType());
                request.setHeader("Connection", "Keep-Alive");                
            }
            
            Log.d(LOG_TAG, "START - Command " + command + " ...");
            long start = System.currentTimeMillis();            
            
            // Send the command, and wait for the response.
            HttpResponse response = m_httpClient.execute(request);
            
            long end = System.currentTimeMillis();
            Log.d(LOG_TAG, "END - Command " + command + ". Time: " + (end - start) + " ms.");            
            
            // Get the status and the response.
            int statusCode = response.getStatusLine().getStatusCode();
            if(outputFile.equals(""))
            {
                responseText = getResponseText(response);
                Log.d(LOG_TAG, "Response obtained, status: " + response.getStatusLine() + ", response: " + responseText);
            }
            else
            {
                responseText = getResponseFile(response, outputFile);
                Log.d(LOG_TAG, "Response obtained, status: " + response.getStatusLine());
            }
            
            
            // If the command wasn't properly handled, it will have to be handled higher up.
            if(statusCode != HTTP_RESPONSE_OKAY_CODE)
            {
                // By default we will return the response as the error.
                String errorMessage = responseText;
                
                // Check if the response is formatted to give a more specific error.
                String messageStartChar = "{{";
                String messageEndChar = "}}";
                int messageStartPos = responseText.indexOf(messageStartChar);
                int messageEndPos = responseText.indexOf(messageEndChar);                
                if(messageStartPos != -1 && messageEndPos != -1)
                {
                    // If so, get it.
                    errorMessage = responseText.substring(messageStartPos + messageStartChar.length(), messageEndPos);
                }
                
                // Throw an exception with the error.
                throw new CloudletCommandException("Command " + command + " returned an error code " + statusCode + ". Details: " + errorMessage);
            }
        } 
        catch (ClientProtocolException e) 
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
            throw new CloudletCommandException("Error sending command: " + e.getMessage());
        } 
        catch (IOException e) 
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
            throw new CloudletCommandException("Error sending command: " + e.getMessage());
        }

        return responseText;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Returns the full URI for an HTTP command.
     * @param command The command to be sent, without the preceding server name and HTTP prefixes.
     * @return A full URI including the HTTP prefixes and server name.
     */
    private URI getCommandURI(final String command)
    {
        URI fullURI = null;       
        try
        {
            fullURI = new URI(m_cloudletURI + command);
        }
        catch (URISyntaxException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }        

        return fullURI;
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Gets the response text from an HTTP response as String.
     * @param response The HTTP response to get the text from.
     * @return The text in the response as a string.
     */
    private String getResponseText(final HttpResponse response)
    {
        String responseText = "";
        
        // Return empty in this case.
        if (response == null)
        {
            return responseText;
        }
        
        try
        {
            final InputStream responseContentInputStream = response.getEntity().getContent();
            if (responseContentInputStream != null)
            {
                // Load the response from the input stream into a byte buffer.
                int size = (int) response.getEntity().getContentLength();
                byte[] resByteBuf = new byte[size];
                responseContentInputStream.read(resByteBuf);
                responseContentInputStream.close();

                // Turn the buffer into a string, which should be straightforward since HTTP uses strings to communicate.
                responseText = new String(resByteBuf);
            }
        }
        catch (IllegalStateException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        catch (IOException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        return responseText;
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Gets the response file from an HTTP response.
     * @param response The HTTP response to get the text from.
     * @return The path of the file stored.
     */
    private String getResponseFile(final HttpResponse response, final String filePath)
    {
        String outputFilepath = "";
        
        // Return empty in this case.
        if (response == null)
        {
            return outputFilepath;
        }
        
        try
        {
            final InputStream responseContentInputStream = response.getEntity().getContent();
            if (responseContentInputStream != null)
            {
                // Create an output file.
                File file = new File(filePath);
                OutputStream os = new FileOutputStream(file);

                // Write the file info into the new file.
                int len1=0;
                byte[] resByteBuf = new byte[1024];
                while( (len1=responseContentInputStream.read(resByteBuf)) >0 )
                {
                    os.write(resByteBuf, 0, len1);
                }
                os.close();
                responseContentInputStream.close();  
                
                outputFilepath = filePath;
            }
        }
        catch (IllegalStateException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        catch (IOException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        return outputFilepath;
    }    
}

package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.Cloudlet;
import edu.cmu.sei.ams.cloudlet.CloudletError;
import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.impl.cmds.GetServicesCommand;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.methods.HttpRequestBase;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONObject;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetAddress;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

/**
 * User: jdroot
 * Date: 3/19/14
 * Time: 4:05 PM
 */
public class CloudletImpl implements Cloudlet, CloudletCommandExecutor
{
    private static final XLogger log = XLoggerFactory.getXLogger(CloudletImpl.class);

    private final String name;
    private final InetAddress addr;
    private final int port;

    public CloudletImpl(String name, InetAddress addr, int port)
    {
        this.name = name;
        this.addr = addr;
        this.port = port;
    }

    @Override
    public String getName()
    {
        return name;
    }

    @Override
    public InetAddress getAddress()
    {
        return addr;
    }

    @Override
    public int getPort()
    {
        return port;
    }

    @Override
    public List<Service> getServices() throws Exception
    {
        log.entry();

        String result = executeCommand(new GetServicesCommand()); //CloudletCommand.GET_SERVICES.execute(this);

        List<Service> ret = new ArrayList<Service>();

        JSONObject obj = new JSONObject(result);
        JSONArray services = obj.getJSONArray("services");
        for (int x = 0; x < services.length(); x++)
        {
            JSONObject service = services.getJSONObject(x);
            ret.add(new ServiceImpl(this, service));
        }

        log.exit(ret);
        return ret;
    }

    @Override
    public String executeCommand(edu.cmu.sei.ams.cloudlet.impl.cmds.CloudletCommand cmd) throws CloudletError
    {
        log.entry(cmd.getMethod(), cmd.getPath());

        HttpClient client = null;

        String command = String.format("http://%s:%d/api%s",
                getAddress().getHostAddress(),
                getPort(),
                cmd.getPath());

        String args = null;
        for (String key : cmd.getArgs().keySet())
        {
            if (args == null)
                args = "?";
            args += key + "=" + cmd.getArgs().get(key);
        }

        if (args != null)
            command += args;

        log.info("Compiled command: " + command);

        HttpRequestBase request;
        switch (cmd.getMethod())
        {
            case GET:
                request = new HttpGet();
                break;
            case PUT:
                request = new HttpPut();
                break;
            case POST:
                request = new HttpPost();
                break;
            default:
                log.exit("");
                return "";
        }

        try
        {

            client = new DefaultHttpClient();

            request.setURI(new URI(command));

            HttpResponse response = client.execute(request);

            int code = response.getStatusLine().getStatusCode();
            String responseText = getResponseText(response);

            log.info("Response object: " + response.getStatusLine().getReasonPhrase());

            if (code != 200)
                throw new CloudletError(response.getStatusLine() + (responseText == null ? "" : ":\n" + responseText));

            log.exit(responseText);
            return responseText;
        }
        catch (CloudletError e)
        {
            throw e; //Just pass it on
        }
        catch (Exception e)
        {
            log.error("Error connecting to server!", e);
            throw new CloudletError("Error sending command to server!", e);
        }
        finally
        {
            if (client != null)
            {
                try
                {
                    client.getConnectionManager().shutdown();
                }
                catch (Exception e)
                {
                    log.error("Error shutting down http client");
                }
            }
        }
    }

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
                if (size <= 0)
                    return null;
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

    public String toString()
    {
        return name + "[" + addr + ":" + port + "]";
    }
}

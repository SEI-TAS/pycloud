package edu.cmu.sei.ams.cloudlet;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.methods.HttpRequestBase;
import org.apache.http.impl.client.DefaultHttpClient;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 4:35 PM
 */
public class CloudletCommand
{
    private static final XLogger log = XLoggerFactory.getXLogger(CloudletCommand.class);

    private static final String STATIC_PATH = "/api";

    static final CloudletCommand GET_SERVICES = new CloudletCommand(Method.GET, "/servicevm/listServices");

    private static enum Method
    {
        GET,
        PUT,
        POST
    }

    private final Method method;
    private final String path;

    private CloudletCommand(Method method, String path)
    {
        this.method = method;
        this.path = STATIC_PATH + path;
    }

    String execute(Cloudlet cloudlet) throws CloudletError
    {
        log.entry(cloudlet, method, path);

        HttpClient client = null;

        String command = String.format("http://%s:%d%s",
                cloudlet.getAddress().getHostAddress(),
                cloudlet.getPort(),
                path);

        log.info("Compiled command: " + command);

        HttpRequestBase request;
        switch (method)
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
}

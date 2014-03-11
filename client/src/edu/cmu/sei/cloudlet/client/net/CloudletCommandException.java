package edu.cmu.sei.cloudlet.client.net;

/**
 * Simple class to handle exceptions when sending Cloudlet commands.
 * @author secheverria
 *
 */
public class CloudletCommandException extends Exception
{
    private static final long serialVersionUID = 1L;

    public CloudletCommandException(String message) 
    {
        super(message);
    }
}

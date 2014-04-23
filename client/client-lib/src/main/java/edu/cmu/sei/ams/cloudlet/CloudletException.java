package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 4:22 PM
 * CloudletException can happen when there is an issue with a cloudlet command
 */
public class CloudletException extends Exception
{
    public CloudletException(String message)
    {
        super(message);
    }

    public CloudletException(String message, Throwable cause)
    {
        super(message, cause);
    }
}

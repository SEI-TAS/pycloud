package edu.cmu.sei.ams.cloudlet.impl.cmds;

import edu.cmu.sei.ams.cloudlet.impl.HttpMethod;

import java.util.HashMap;
import java.util.Map;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 2:50 PM
 * Parent class for all Cloudlet commands. It facilitates URL args and file uploads
 */
public abstract class CloudletCommand
{
    private Map<String, String> args = new HashMap<String, String>();

    public abstract String getPath();

    public Map<String, String> getArgs()
    {
        return args;
    }

    public HttpMethod getMethod()
    {
        return HttpMethod.GET;
    }

    public boolean hasFile()
    {
        return false;
    }

}

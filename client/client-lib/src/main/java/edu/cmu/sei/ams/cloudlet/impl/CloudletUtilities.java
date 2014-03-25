package edu.cmu.sei.ams.cloudlet.impl;

import org.json.JSONObject;

/**
 * User: jdroot
 * Date: 3/21/14
 * Time: 10:04 AM
 */
public class CloudletUtilities
{
    static String getSafeString(String name, JSONObject json)
    {
        if (json.has(name))
            return json.getString(name);
        return null;
    }
}

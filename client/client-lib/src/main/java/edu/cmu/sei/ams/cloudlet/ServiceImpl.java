package edu.cmu.sei.ams.cloudlet;

import org.json.JSONObject;
import static edu.cmu.sei.ams.cloudlet.CloudletUtilities.*;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 3:44 PM
 */
public class ServiceImpl implements Service
{
    private String serviceId;
    private String description;

    ServiceImpl(JSONObject json)
    {
        this.serviceId = getSafeString("_id", json);
        this.description = getSafeString("description", json);
    }

    @Override
    public String getServiceId()
    {
        return serviceId;
    }

    @Override
    public String getDescription()
    {
        return description;
    }

    @Override
    public String toString()
    {
        return "{serviceId:\"" + serviceId + "\"," +
                "description:\"" + description + "\"}";
    }
}

package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.CloudletError;
import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.VMInfo;
import edu.cmu.sei.ams.cloudlet.impl.cmds.StartServiceCommand;
import org.json.JSONObject;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;


import static edu.cmu.sei.ams.cloudlet.impl.CloudletUtilities.*;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 3:44 PM
 */
public class ServiceImpl implements Service
{
    private static final XLogger log = XLoggerFactory.getXLogger(ServiceImpl.class);

    private String serviceId;
    private String description;

    private final CloudletCommandExecutor mCloudlet;

    ServiceImpl(CloudletCommandExecutor mCloudlet, JSONObject json)
    {
        this.serviceId = getSafeString("_id", json);
        this.description = getSafeString("description", json);
        this.mCloudlet = mCloudlet;
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
    public VMInfo startService()
    {
        VMInfo ret = null;
        StartServiceCommand cmd = new StartServiceCommand(this);
        try
        {
            String jsonStr = mCloudlet.executeCommand(cmd);
            JSONObject obj = new JSONObject(jsonStr);
            ret = new VMInfoImpl(mCloudlet, this, obj);
        }
        catch (CloudletError e)
        {
            log.error("Error starting service", e);
        }
        return ret;
    }

    @Override
    public String toString()
    {
        return "{serviceId:\"" + serviceId + "\"," +
                "description:\"" + description + "\"}";
    }
}

package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.VMInfo;
import org.json.JSONObject;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import java.net.InetAddress;

import static edu.cmu.sei.ams.cloudlet.impl.CloudletUtilities.*;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 4:34 PM
 */
public class VMInfoImpl implements VMInfo
{
    private static final XLogger log = XLoggerFactory.getXLogger(VMInfoImpl.class);
    private String instanceId;
    private InetAddress addr;
    private int port;

    private Service service;
    private final CloudletCommandExecutor mCloudlet;

    VMInfoImpl(CloudletCommandExecutor mCloudlet, Service service, JSONObject obj)
    {
        log.entry(mCloudlet, service, obj);
        this.mCloudlet = mCloudlet;
        this.instanceId = getSafeString("INSTANCE_ID", obj);
        this.port = getSafeInt("PORT", obj);
        this.addr = getSafeInetAddress("IP_ADDRESS", obj);
        this.service = service;
        log.exit();
    }

    @Override
    public String getServiceId()
    {
        return service.getServiceId();
    }

    @Override
    public String getInstanceId()
    {
        return instanceId;
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
    public String toString()
    {
        return "{serviceId:\"" + getServiceId() + "\", instanceId:\"" + getInstanceId() + "\", ip_address:\"" + getAddress() + "\", port:" + getPort() + "}";
    }
}

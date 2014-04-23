package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.ServiceVM;
import edu.cmu.sei.ams.cloudlet.impl.cmds.StopVMInstanceCommand;
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
public class ServiceVMImpl implements ServiceVM
{
    private static final XLogger log = XLoggerFactory.getXLogger(ServiceVMImpl.class);
    private String instanceId;
    private InetAddress addr;
    private int port;

    private Service mService;
    private final CloudletCommandExecutor mCloudlet;

    ServiceVMImpl(CloudletCommandExecutor mCloudlet, Service mService, JSONObject obj)
    {
        log.entry(mCloudlet, mService, obj);
        this.mCloudlet = mCloudlet;
        this.instanceId = getSafeString("INSTANCE_ID", obj);
        this.port = getSafeInt("PORT", obj);
        this.addr = getSafeInetAddress("IP_ADDRESS", obj);
        this.mService = mService;
        log.exit();
    }

    /**
     * {@inheritDoc}
     * @return
     */
    @Override
    public boolean stopVm()
    {
        try
        {
            StopVMInstanceCommand cmd = new StopVMInstanceCommand(this);
            String result = mCloudlet.executeCommand(cmd);
            if ("OK".equals(result))
                return true;
            else
                return false;
        }
        catch (Exception e)
        {
            log.error("Error stopping VM!", e);
            return false;
        }
    }

    /**
     * {@inheritDoc}
     * @return
     */
    @Override
    public String getServiceId()
    {
        return mService.getServiceId();
    }

    /**
     * {@inheritDoc}
     * @return
     */
    @Override
    public String getInstanceId()
    {
        return instanceId;
    }

    /**
     * {@inheritDoc}
     * @return
     */
    @Override
    public InetAddress getAddress()
    {
        return addr;
    }

    /**
     * {@inheritDoc}
     * @return
     */
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

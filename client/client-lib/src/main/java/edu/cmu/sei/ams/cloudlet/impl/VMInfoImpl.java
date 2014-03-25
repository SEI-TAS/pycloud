package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.VMInfo;

import java.net.InetAddress;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 4:34 PM
 */
public class VMInfoImpl implements VMInfo
{

    VMInfoImpl()
    {

    }

    @Override
    public String getServiceId()
    {
        throw new UnsupportedOperationException("VMInfoImpl#getServiceId is unsupported at this time");
    }

    @Override
    public String getInstanceId()
    {
        throw new UnsupportedOperationException("VMInfoImpl#getInstanceId is unsupported at this time");
    }

    @Override
    public InetAddress getAddress()
    {
        throw new UnsupportedOperationException("VMInfoImpl#getAddress is unsupported at this time");
    }

    @Override
    public int getPort()
    {
        throw new UnsupportedOperationException("VMInfoImpl#getPort is unsupported at this time");
    }
}

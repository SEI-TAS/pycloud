package edu.cmu.sei.ams.cloudlet;

import java.net.InetAddress;

/**
 * User: jdroot
 * Date: 3/19/14
 * Time: 4:05 PM
 */
public class CloudletImpl implements Cloudlet
{
    private final String name;
    private final InetAddress addr;
    private final int port;

    CloudletImpl(String name, InetAddress addr, int port)
    {
        this.name = name;
        this.addr = addr;
        this.port = port;
    }

    @Override
    public String getName()
    {
        return name;
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

    public String toString()
    {
        return name + "[" + addr + ":" + port + "]";
    }
}

package edu.cmu.sei.ams.cloudlet;

import java.net.InetAddress;
import java.util.List;

/**
 * User: jdroot
 * Date: 3/19/14
 * Time: 1:28 PM
 */
public interface Cloudlet
{
    public String getName();
    public InetAddress getAddress();
    public int getPort();
    public List<Service> getServices() throws Exception;
}

package edu.cmu.sei.ams.cloudlet;

import java.net.InetAddress;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 4:11 PM
 */
public interface ServiceVM
{
    public String getServiceId();
    public String getInstanceId();
    public InetAddress getAddress();
    public int getPort();

    public boolean stopVm();
}

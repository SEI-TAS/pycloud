package edu.cmu.sei.ams.cloudlet;

import java.net.InetAddress;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 4:11 PM
 * Immutable representation of a running service on a Cloudlet
 */
public interface ServiceVM
{
    /**
     * The ID of the service this instance was created from
     */
    public String getServiceId();

    /**
     * The specific ID of this running service
     * @return
     */
    public String getInstanceId();

    /**
     * Returns the address that this service is running on
     * @return
     */
    public InetAddress getAddress();

    /**
     * Returns the port that this service is running on
     * @return
     */
    public int getPort();

    /**
     * Will stop this instance of the service
     * @return
     */
    public boolean stopVm();
}

package edu.cmu.sei.ams.cloudlet;

import java.net.InetAddress;
import java.util.List;

/**
 * User: jdroot
 * Date: 3/19/14
 * Time: 1:28 PM
 *
 * This interface is an immutable representation of an existing Cloudlet server
 */
public interface Cloudlet
{
    /**
     * Gets the name of this Cloudlet
     * @return the name of this Cloudlet
     */
    public String getName();

    /**
     * Gets the address of this Cloudlet
     * @return address of this Cloudlet
     */
    public InetAddress getAddress();

    /**
     * Gets the port this cloudlet is listening on
     * @return port
     */
    public int getPort();

    /**
     * Gets a list of services available on this Cloudlet
     * @return
     * @throws Exception can throw exceptions when server is unreachable or bad data is returned
     */
    public List<Service> getServices() throws CloudletException;
}

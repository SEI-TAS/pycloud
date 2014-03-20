package edu.cmu.sei.ams.cloudlet;

import java.net.InetAddress;

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
}

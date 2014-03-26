package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 3:44 PM
 */
public interface Service
{
    public String getServiceId();
    public String getDescription();

    public ServiceVM startService();
}

package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 4/8/14
 * Time: 11:45 AM
 */
public interface CpuInfo
{
    /**
     * Returns the total cores of the server, including virtual cores
     * @return
     */
    public int getTotalCores();

    /**
     * Returns the current CPU usage of the Cloudlet as a percent (This number can be greater than 100.0)
     * @return
     */
    public double getUsage();
}

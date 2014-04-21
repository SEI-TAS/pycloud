package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 4/8/14
 * Time: 11:44 AM
 */
public interface CloudletSystemInfo
{
    /**
     * Returns the current CPU usage of the Cloudlet
     * @return
     */
    public CpuInfo getCPUInfo();

    /**
     * Returns the current memory usage of the Cloudlet
     * @return
     */
    public MemoryInfo getMemoryInfo();
}

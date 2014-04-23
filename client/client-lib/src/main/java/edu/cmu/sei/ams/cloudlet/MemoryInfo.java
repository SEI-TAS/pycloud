package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 4/8/14
 * Time: 11:45 AM
 */
public interface MemoryInfo
{
    /**
     * Returns the maximum system memory for the Cloudlet in bytes
     * @return
     */
    public long getMaxMemory();

    /**
     * Returns the current amount of free memory in bytes
     * @return
     */
    public long getFreeMemory();
}

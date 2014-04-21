package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.CloudletSystemInfo;
import edu.cmu.sei.ams.cloudlet.CpuInfo;
import edu.cmu.sei.ams.cloudlet.MemoryInfo;
import org.json.JSONObject;
import static edu.cmu.sei.ams.cloudlet.impl.CloudletUtilities.*;

/**
 * User: jdroot
 * Date: 4/8/14
 * Time: 11:47 AM
 */
public class CloudletSystemInfoImpl implements CloudletSystemInfo
{

    private final CpuInfo cpuInfo;
    private final MemoryInfo memoryInfo;

    CloudletSystemInfoImpl(JSONObject obj)
    {
        this.cpuInfo = new CpuInfoImpl(getSafeJsonObject("cpu_info", obj));
        this.memoryInfo = new MemoryInfoImpl(getSafeJsonObject("memory_info", obj));
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public CpuInfo getCPUInfo()
    {
        return cpuInfo;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public MemoryInfo getMemoryInfo()
    {
        return memoryInfo;
    }

    @Override
    public String toString()
    {
        return "{cpu_info:" + getCPUInfo() + ",memory_info:" + getMemoryInfo() + "}";
    }
}

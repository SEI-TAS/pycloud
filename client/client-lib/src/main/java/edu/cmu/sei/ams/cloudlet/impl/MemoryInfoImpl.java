package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.MemoryInfo;
import org.json.JSONObject;
import static edu.cmu.sei.ams.cloudlet.impl.CloudletUtilities.*;

/**
 * User: jdroot
 * Date: 4/8/14
 * Time: 11:47 AM
 */
public class MemoryInfoImpl implements MemoryInfo
{

    private final long maxMemory;
    private final long freeMemory;

    MemoryInfoImpl(JSONObject json)
    {
        maxMemory = getSafeLong("max_memory", json);
        freeMemory = getSafeLong("free_memory", json);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public long getMaxMemory()
    {
        return maxMemory;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public long getFreeMemory()
    {
        return freeMemory;
    }

    @Override
    public String toString()
    {
        return "{max_memory:" + getMaxMemory() + ",free_memory:" + getFreeMemory() + "}";
    }
}

package edu.cmu.sei.ams.cloudlet;

import org.json.JSONArray;
import org.json.JSONObject;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;

/**
 * User: jdroot
 * Date: 3/19/14
 * Time: 4:05 PM
 */
public class CloudletImpl implements Cloudlet
{
    private static final XLogger log = XLoggerFactory.getXLogger(CloudletImpl.class);

    private final String name;
    private final InetAddress addr;
    private final int port;

    CloudletImpl(String name, InetAddress addr, int port)
    {
        this.name = name;
        this.addr = addr;
        this.port = port;
    }

    @Override
    public String getName()
    {
        return name;
    }

    @Override
    public InetAddress getAddress()
    {
        return addr;
    }

    @Override
    public int getPort()
    {
        return port;
    }

    @Override
    public List<Service> getServices() throws Exception
    {
        log.entry();

        String result = CloudletCommand.GET_SERVICES.execute(this);

        List<Service> ret = new ArrayList<Service>();

        JSONObject obj = new JSONObject(result);
        JSONArray services = obj.getJSONArray("services");
        for (int x = 0; x < services.length(); x++)
        {
            JSONObject service = services.getJSONObject(x);
            ret.add(new ServiceImpl(service));
        }

        log.exit(ret);
        return ret;
    }

    public String toString()
    {
        return name + "[" + addr + ":" + port + "]";
    }
}

package edu.cmu.sei.ams.cloudlet;

import org.codehaus.jackson.annotate.JsonAutoDetect;
import org.codehaus.jackson.annotate.JsonMethod;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import org.json.simple.parser.JSONParser;
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

        JSONObject obj = (JSONObject)JSONValue.parse(result);
        JSONArray services = (JSONArray)obj.get("services");
        ObjectMapper mapper = new ObjectMapper();
        mapper.setVisibility(JsonMethod.FIELD, JsonAutoDetect.Visibility.ANY);
        mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        for (Object service : services)
        {
            Service s = mapper.readValue(service.toString(), ServiceImpl.class);
            ret.add(s);
        }






        log.exit(ret);
        return ret;
    }

    public String toString()
    {
        return name + "[" + addr + ":" + port + "]";
    }
}

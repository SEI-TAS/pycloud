package edu.cmu.sei.ams.cloudlet;

import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import javax.jmdns.JmDNS;
import javax.jmdns.ServiceInfo;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;

import static edu.cmu.sei.ams.cloudlet.Constants.*;

/**
 * User: jdroot
 * Date: 3/19/14
 * Time: 1:35 PM
 */
public class CloudletFinder
{
    private static final XLogger log = XLoggerFactory.getXLogger(CloudletFinder.class);

    public static List<Cloudlet> findCloudlets() throws Exception
    {
        log.entry();
        List<Cloudlet> ret = new ArrayList<Cloudlet>();
        JmDNS jmdns = JmDNS.create(InetAddress.getByName("255.255.255.255"));
        ServiceInfo[] info = jmdns.list(CLOUDLET_SERVER_DNS);

        for (ServiceInfo i : info)
        {
            String name = i.getName();
            InetAddress addr = i.getInetAddresses()[0];
            int port = i.getPort();
            ret.add(new CloudletImpl(name, addr, port));
        }
        log.exit(ret);
        return ret;
    }
}

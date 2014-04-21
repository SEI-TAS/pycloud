package edu.cmu.sei.ams.cloudlet.rank;

import edu.cmu.sei.ams.cloudlet.Cloudlet;
import edu.cmu.sei.ams.cloudlet.CloudletException;
import edu.cmu.sei.ams.cloudlet.CloudletSystemInfo;
import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.ams.cloudlet.impl.CloudletImpl;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

/**
 * Attempts to rank the cloudlet based on how much free CPU power there is.
 * This calculation is done with: (max_cores * 100.0) - usage
 * User: jdroot
 * Date: 4/4/14
 * Time: 3:45 PM
 */
public class CpuBasedRanker implements CloudletRanker
{
    private static final XLogger log = XLoggerFactory.getXLogger(CpuBasedRanker.class);

    @Override
    public double rankCloudlet(Service service, Cloudlet cloudlet) throws CloudletException
    {
        log.entry(service, cloudlet);
        CloudletSystemInfo info = cloudlet.getSystemInfo();
        double ranking = (100.0 * info.getCPUInfo().getTotalCores()) - info.getCPUInfo().getUsage();
        log.exit(ranking);
        return ranking;
    }
}

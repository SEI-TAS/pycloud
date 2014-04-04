package edu.cmu.sei.ams.cloudlet.rank;

import edu.cmu.sei.ams.cloudlet.Cloudlet;
import edu.cmu.sei.ams.cloudlet.Service;

/**
 * User: jdroot
 * Date: 4/4/14
 * Time: 3:45 PM
 */
public class CpuBasedRanker implements CloudletRanker
{

    @Override
    public double rankCloudlet(Service service, Cloudlet cloudlet)
    {
        return 1.0;
    }
}

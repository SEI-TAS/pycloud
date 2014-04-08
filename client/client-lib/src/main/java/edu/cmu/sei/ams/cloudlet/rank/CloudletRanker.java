package edu.cmu.sei.ams.cloudlet.rank;

import edu.cmu.sei.ams.cloudlet.Cloudlet;
import edu.cmu.sei.ams.cloudlet.CloudletException;
import edu.cmu.sei.ams.cloudlet.Service;

/**
 * User: jdroot
 * Date: 4/2/14
 * Time: 10:06 AM
 * Implementations of CloudletRanker provide the ability to rank Cloudlets
 */
public interface CloudletRanker
{
    public double rankCloudlet(Service service, Cloudlet cloudlet) throws CloudletException;
}

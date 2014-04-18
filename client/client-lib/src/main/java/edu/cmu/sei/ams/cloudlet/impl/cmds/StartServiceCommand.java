package edu.cmu.sei.ams.cloudlet.impl.cmds;

import edu.cmu.sei.ams.cloudlet.Service;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 3:39 PM
 * The start services command
 */
public class StartServiceCommand extends CloudletCommand
{

    private static final String CMD = "/servicevm/start";

    public StartServiceCommand(Service mService)
    {
        getArgs().put("serviceId", mService.getServiceId());
    }

    public void setIsolated(boolean isolated)
    {
        getArgs().put("isolated", "" + isolated);
    }

    @Override
    public String getPath()
    {
        return CMD;
    }
}

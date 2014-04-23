package edu.cmu.sei.ams.cloudlet.impl.cmds;

import edu.cmu.sei.ams.cloudlet.ServiceVM;

/**
 * User: jdroot
 * Date: 3/25/14
 * Time: 5:00 PM
 * The stop vm command
 */
public class StopVMInstanceCommand extends CloudletCommand
{

    private static final String CMD = "/servicevm/stop";

    public StopVMInstanceCommand(ServiceVM vm)
    {
        getArgs().put("instanceId", vm.getInstanceId());
    }

    @Override
    public String getPath()
    {
        return CMD;
    }
}

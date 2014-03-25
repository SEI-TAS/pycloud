package edu.cmu.sei.ams.cloudlet.impl.cmds;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 2:51 PM
 */
public class GetServicesCommand extends CloudletCommand
{
    private static final String CMD = "/servicevm/listServices";

    @Override
    public String getPath()
    {
        return CMD;
    }
}

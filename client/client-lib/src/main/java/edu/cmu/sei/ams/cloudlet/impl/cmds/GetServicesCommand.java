package edu.cmu.sei.ams.cloudlet.impl.cmds;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 2:51 PM
 * The get services command. It is a simple get command that only needs to override the path
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

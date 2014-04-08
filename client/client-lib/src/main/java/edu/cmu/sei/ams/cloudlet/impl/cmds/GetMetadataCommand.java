package edu.cmu.sei.ams.cloudlet.impl.cmds;

/**
 * User: jdroot
 * Date: 4/8/14
 * Time: 2:15 PM
 */
public class GetMetadataCommand extends CloudletCommand
{
    private static final String CMD = "/cloudlet_info";

    @Override
    public String getPath()
    {
        return CMD;
    }
}

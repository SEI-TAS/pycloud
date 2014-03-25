package edu.cmu.sei.ams.cloudlet.impl;

import edu.cmu.sei.ams.cloudlet.CloudletError;

/**
 * User: jdroot
 * Date: 3/24/14
 * Time: 3:18 PM
 */
public interface CloudletCommandExecutor
{
    public String executeCommand(edu.cmu.sei.ams.cloudlet.impl.cmds.CloudletCommand cmd) throws CloudletError;
}

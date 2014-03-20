package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 3:44 PM
 */
public class ServiceImpl implements Service
{
    private String _id;
    private String description;

    @Override
    public String getServiceId()
    {
        return _id;
    }

    @Override
    public String getDescription()
    {
        return description;
    }
}

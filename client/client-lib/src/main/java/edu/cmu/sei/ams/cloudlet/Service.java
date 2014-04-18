package edu.cmu.sei.ams.cloudlet;

/**
 * User: jdroot
 * Date: 3/20/14
 * Time: 3:44 PM
 * Immutable representation of a service a Cloudlet is capable of providing
 */
public interface Service
{
    /**
     * Gets the Service ID for a specific service
     * @return
     */
    public String getServiceId();

    /**
     * Gets the textual description of this service
     * @return
     */
    public String getDescription();

    /**
     * Asks the server to start the service. Blocks until the service is started.
     * This action will attempt to join an existing VM by default.
     * @return Immutable instance of the information regarding the started service
     */
    public ServiceVM startService();

    /**
     * Asks the server to start the service. Blocks until the service is started.
     * @param join Specifies if we should join an existing VM or not
     * @return Immutable instance of the information regarding the started service
     */
    public ServiceVM startService(boolean join);

    /**
     * Stops an instance of this service<br/>
     * Should eventually be removed
     * @return wether or not the service was stopped
     */
    public boolean stopService();

    /**
     * Gets the current instance of the running vm, if one exists<br/>
     * Should eventually be removed
     * @return Null if the running instance doesnt exist, ServiceVM if it does
     */
    public ServiceVM getServiceVM();
}

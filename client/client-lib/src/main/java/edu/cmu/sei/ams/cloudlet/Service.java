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
     * @return Immutable instance of the information regarding the started service
     */
    public ServiceVM startService();

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

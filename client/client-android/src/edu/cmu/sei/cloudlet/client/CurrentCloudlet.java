package edu.cmu.sei.cloudlet.client;

import edu.cmu.sei.ams.cloudlet.Cloudlet;

/**
 * 
 * This is a in-memory class used to store the cloudlet information.
 * It has public static members so the information about the currently selected
 * cloudlet can be shared easily between activities.
 * 
 * @author ssimanta, secheverria
 * 
 */
public class CurrentCloudlet
{
    public static Cloudlet cloudlet;

    // The IP and port. Static so that it can be easily shared between activities.
    public static String name = "";
    public static String ipAddress = "";
    public static int port = 0;

    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Checks if the current cloudlet info is valid.
     * @return true if it is valid, false if not.
     */
    public static boolean isValid()
    {
        return !name.equals("") && !ipAddress.equals("") && !(port == 0);
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns the cloudlet info as a string.
     */    
    public static String getAsString()
    {
        return "[Name: " + name + ", IP: " + ipAddress + " , PORT: " + port + "]";
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns an HTTP URI to connect to the cloudlet.
     * @return
     */
    public static String getHttpURI()
    {
        return "http://" + ipAddress + ":" + port + "/";
    }
}

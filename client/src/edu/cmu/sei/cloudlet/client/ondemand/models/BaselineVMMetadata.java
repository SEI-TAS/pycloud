package edu.cmu.sei.cloudlet.client.ondemand.models;

import java.io.File;

import org.json.JSONException;
import org.json.JSONObject;

import edu.cmu.sei.cloudlet.client.FileUtils;

import android.util.Log;

/**
 * Class that stores the metadata information about a Server VM which a cloudlet-ready app will connect to.
 * @author secheverria
 *
 */
public class BaselineVMMetadata
{
    public static final String LOG_TAG = BaselineVMMetadata.class.getName();

    public static final String OS_DATA_KEY = "osData";
    public static final String OS_FAMILY_KEY = "osFamily";
    public static final String OS_KEY = "os";
    public static final String OS_VERSION_KEY = "osVersion";
    public static final String OS_ISA_KEY = "osISA";

    protected String osFamily = "Any";
    protected String os = "Any";
    protected String osVersion = "Any";
    protected String osISA = "Any";

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public BaselineVMMetadata(final JSONObject jsonObj)
    {
        loadFromJson(jsonObj);
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public BaselineVMMetadata(final String filePath)
    {
        loadFromFile(filePath);
    }       

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String getOsFamily()
    {
        return osFamily;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String getOs()
    {
        return os;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String getOsVersion()
    {
        return osVersion;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String getOsISA()
    {
        return osISA;
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public String toString()
    {
        return writeToJson().toString();
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    private void loadFromJson(final JSONObject rootJSONObject)
    {
        if (rootJSONObject != null)
        {
            try
            {
                JSONObject serviceVmJSONObject = rootJSONObject.getJSONObject(OS_DATA_KEY);
                
                if(serviceVmJSONObject != null)
                {
                    this.osFamily = serviceVmJSONObject.getString(OS_FAMILY_KEY);
                    this.os = serviceVmJSONObject.getString(OS_KEY);
                    this.osVersion = serviceVmJSONObject.getString(OS_VERSION_KEY);
                    this.osISA = serviceVmJSONObject.getString(OS_ISA_KEY);                    
                }

            }
            catch (JSONException e)
            {
                e.printStackTrace();
            }
        }        
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public JSONObject writeToJson()
    {
        // Create a new JSON object and put the data there
        JSONObject rootJSONObj = new JSONObject();
        try
        {
            JSONObject serviceVmJSONObject = new JSONObject();
            rootJSONObj.put(OS_DATA_KEY, serviceVmJSONObject);
            
            serviceVmJSONObject.put(OS_FAMILY_KEY, osFamily);
            serviceVmJSONObject.put(OS_KEY, os);
            serviceVmJSONObject.put(OS_VERSION_KEY, osVersion);
            serviceVmJSONObject.put(OS_ISA_KEY, osISA);
        }
        catch (JSONException e)
        {
            e.printStackTrace();
        }
        
        return rootJSONObj;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public boolean writeToFile(String fileName)
    {
        String jsonString = writeToJson().toString();
        return FileUtils
                .writeStringtoDataFile(jsonString, fileName);
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    public boolean loadFromFile(String fileName)
    {
        if (fileName == null)
        {
            Log.e(LOG_TAG, "Input file name to loadFromFile is null. ");
            return false;
        }

        // Check if the file exists.
        File file = new File(fileName);
        if (!file.exists())
        {
            Log.e(LOG_TAG, "Input file [" + fileName + "] to doesn't exist.");
            return false;
        }

        // Load the text.
        String fileContents = FileUtils.parseDataFileToString(fileName);
        if (fileContents == null || fileContents.trim().length() == 0)
        {
            Log.e(LOG_TAG, "Input file [" + fileName + "] is empty.");
            return false;
        }

        // Turn into a JSON structure, and load from there.
        try
        {
            JSONObject rootJSONObject = new JSONObject(fileContents);
            loadFromJson(rootJSONObject);
        }
        catch (JSONException e)
        {
            e.printStackTrace();
        }

        // if you got here all is well.
        return true;
    }
}

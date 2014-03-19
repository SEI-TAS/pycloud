package edu.cmu.sei.cloudlet.client.synth.models;

import java.io.File;

import org.json.JSONException;
import org.json.JSONObject;

import edu.cmu.sei.cloudlet.client.FileUtils;
import edu.cmu.sei.cloudlet.client.models.ServiceVMMetadata;

public class OverlayInfo
{
    // The files that compose the overlay.
    private String m_metadataFilePath = "";
    private String[] m_imageFilePaths;
    
    // Extensions that identify each type of file.
    private final static String METADATA_EXTENSION = "jsonsvm";
    private final static String OVERLAY_IMAGE_EXTENSION = "xz";
    
    // The amount of image files.
    private final static int IMAGE_FILES_AMOUNT = 2;
    
    // Information about the base VM associated with this Overlay.
    private String m_baseVMId = "";
    
    // Information about the ServerVM associated with this Overlay.
    private ServiceVMMetadata m_serverVMMetadata;
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Loads information about an Overlay from the given folder.
     * @param folderPath The path to the folder where the overlay files are.
     */
    public OverlayInfo(String folderPath)
    {
        // Used to store the file paths of both the disk and state images.
        m_imageFilePaths = new String[IMAGE_FILES_AMOUNT];
        int imageFilesFound = 0;
        
        // Check if this folder actually exists.
        File overlayFolder = new File(folderPath);
        overlayFolder = overlayFolder.getAbsoluteFile();
        if (overlayFolder.exists()) 
        {
            // Loop over files to find each of the expected ones by their extension.
            File[] files = overlayFolder.listFiles();            
            for (int i = 0; i < files.length; ++i) 
            {
                // Get the extension for this file.
                File currentFile = files[i];
                String currentFilename = currentFile.getName();
                String currentFileExtension = currentFilename.substring(currentFilename.lastIndexOf(".") + 1, currentFilename.length());
                
                // Check if we found the metadata file, and if so store its path.
                if(currentFileExtension.equalsIgnoreCase(METADATA_EXTENSION))
                {
                    m_metadataFilePath = currentFile.getAbsolutePath();
                    
                    // Load information from the metadata file.
                    loadMetadataInfo();
                }
                
                // Check if we found an image file, and if so store its path.
                if(currentFileExtension.equalsIgnoreCase(OVERLAY_IMAGE_EXTENSION))
                {
                    // We should only have a certain amount of image files.
                    if(imageFilesFound >= IMAGE_FILES_AMOUNT)
                    {
                        throw new RuntimeException("Error loading image files for overlay: more than 2 image files found.");
                    }
                    
                    // Add the image file to the array.
                    m_imageFilePaths[imageFilesFound++] = currentFile.getAbsolutePath();
                }                
            }
        }
        
        // We should have a certain amount of files.
        if(m_metadataFilePath.equals("") || imageFilesFound != IMAGE_FILES_AMOUNT)
        {
            throw new RuntimeException("Error loading files for overlay: not enough files found.");
        }        
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    private void loadMetadataInfo()
    {
        if(m_metadataFilePath == "")
            return;
        
        // Loads the information inside the metadata file into a JSON file.
        String fileContents = FileUtils.parseDataFileToString(m_metadataFilePath);
        JSONObject rootJSONObject = null;
        try
        {
            rootJSONObject = new JSONObject(fileContents);
        }
        catch (JSONException e1)
        {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }
        
        if (rootJSONObject != null)
        {
            // Load the ServerVM info form the same file.
            m_serverVMMetadata = new ServiceVMMetadata(m_metadataFilePath);
            this.m_baseVMId = m_serverVMMetadata.getRefImageId();
        }
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * A string representation of the overlay info.
     * @return a string with the overlay files info. 
     */
    @Override
    public String toString()
    {
        String overlayFilesText = "Metadata: " + m_metadataFilePath + ";\n" + "Image file 1: " + m_imageFilePaths[0] + ";\n" + "Image file 2" + m_imageFilePaths[1] + ";\n";
        String fullText = "Server VM Metadata: " + overlayFilesText + "\n" + "Base VM Id: " + m_baseVMId + "\n" + m_serverVMMetadata.toString() + "\n" ;
        return fullText;
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_metadataFilePath
     */
    public String getMetadataFilePath()
    {
        return m_metadataFilePath;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_imageFilePaths
     */
    public String[] getImageFilePaths()
    {
        return m_imageFilePaths;
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * @return the m_baseVMId
     */
    public String getBaseVMId()
    {
        return m_baseVMId;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_serverVMInfo
     */
    public ServiceVMMetadata getServiceVMInfo()
    {
        return m_serverVMMetadata;
    }
}

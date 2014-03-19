package edu.cmu.sei.cloudlet.client.ondemand.models;

import java.io.File;

import edu.cmu.sei.cloudlet.client.models.ServiceVMMetadata;

public class ProvisioningModuleInfo
{
    // The files that compose the module.
    private String m_baselineVMMetadataFilePath = "";
    private String m_svmVMMetadataFilePath = "";
    private String m_manifestFilePath = "";
    
    // Extensions that identify each type of file.
    private final static String BLVM_METADATA_EXTENSION = "jsonbmd";
    private final static String SVM_METADATA_EXTENSION = "jsonsvm";
    private final static String MANIFEST_EXTENSION = "pp";
    
    // Loaded metadata related to this 
    private BaselineVMMetadata m_baselineVMMetadata;
    private ServiceVMMetadata m_serverVMMetadata;
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * Loads information about an Module from the given folder.
     * @param folderPath The path to the folder where the module files are.
     */
    public ProvisioningModuleInfo(String folderPath)
    {
        // Check if this folder actually exists.
        File moduleFolder = new File(folderPath);
        moduleFolder = moduleFolder.getAbsoluteFile();
        if (moduleFolder.exists()) 
        {
            // Loop over files to find each of the expected ones by their extension.
            File[] files = moduleFolder.listFiles();            
            for (int i = 0; i < files.length; ++i) 
            {
                // Get the extension for this file.
                File currentFile = files[i];
                String currentFilename = currentFile.getName();
                String currentFileExtension = currentFilename.substring(currentFilename.lastIndexOf(".") + 1, currentFilename.length());
                
                // Check if we found the Baseline VM metadata file, and if so store its path.
                if(currentFileExtension.equalsIgnoreCase(BLVM_METADATA_EXTENSION))
                {
                    // Load information from the blvm metadata file.                    
                    m_baselineVMMetadataFilePath = currentFile.getAbsolutePath();
                    m_baselineVMMetadata = new BaselineVMMetadata(m_baselineVMMetadataFilePath);
                }

                // Check if we found the Service VM metadata file, and if so store its path.
                if(currentFileExtension.equalsIgnoreCase(SVM_METADATA_EXTENSION))
                {
                    // Load information from the blvm metadata file.                    
                    m_svmVMMetadataFilePath = currentFile.getAbsolutePath();
                    m_serverVMMetadata = new ServiceVMMetadata(m_svmVMMetadataFilePath);
                }

                // Check if we found Module file, and if so store its path.
                if(currentFileExtension.equalsIgnoreCase(MANIFEST_EXTENSION))
                {
                    m_manifestFilePath = currentFile.getAbsolutePath();
                }
            }
        }
        
        // We should have a certain amount of files.
        if(m_baselineVMMetadataFilePath.equals("") || m_svmVMMetadataFilePath.equals("") || m_manifestFilePath.equals(""))
        {
            throw new RuntimeException("Error loading files for module: not enough files found.");
        }        
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * A string representation of the module info.
     * @return a string with the module files info. 
     */
    @Override
    public String toString()
    {
        String fullText = "Baseline VM Metadata file: " + m_baselineVMMetadataFilePath + ";\n" +
                          "Service VM Metadata file: " + m_svmVMMetadataFilePath + ";\n" + 
                          "Manifest file file: " + m_manifestFilePath + ";\n" + 
                          "Baseline VM Metadata: " + m_baselineVMMetadata.toString() + "\n" +
                          "Server VM Metadata: " + m_serverVMMetadata.toString() + "\n" ;
        return fullText;
    }    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_metadataFilePath
     */
    public String getBaselineVMMetadataFilePath()
    {
        return m_baselineVMMetadataFilePath;
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_svmVMMetadataFilePath
     */
    public String getServiceVMMetadataFilePath()
    {
        return m_svmVMMetadataFilePath;
    }
    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_manifestFilePath
     */
    public String getManifestFilePath()
    {
        return m_manifestFilePath;
    }
    

    /////////////////////////////////////////////////////////////////////////////////////////////////    
    /**
     * @return the m_baselineVMMetadata
     */
    public BaselineVMMetadata getBaselineVMInfo()
    {
        return m_baselineVMMetadata;
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

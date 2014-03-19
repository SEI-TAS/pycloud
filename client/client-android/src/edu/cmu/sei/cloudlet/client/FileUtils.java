package edu.cmu.sei.cloudlet.client;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;

import android.util.Log;

/**
 * Utility class for dealing with files. 
 * @author ssimanta
 *
 */
public class FileUtils {
	
	public static final String LOG_TAG = FileUtils.class.getName();
	
	public static String parseDataFileToString(final String fileName) {
		try {
			final File file = new File(fileName);
			InputStream stream = new FileInputStream(file);

			int size = stream.available();
			byte[] bytes = new byte[size];
			stream.read(bytes);
			stream.close();

			return new String(bytes);

		} catch (IOException e) {
			Log.e(LOG_TAG, "IOException in reading data file  " + fileName + " \n" + e.getMessage());
		}
		return null;
	}
	
	public static boolean writeStringtoDataFile(final String contents,
			final String fileName) {
		// First create the folder structure if necessary.
		File fileToWrite = new File(fileName);
		fileToWrite.mkdirs();		
		
		FileWriter fileWriter = null;
		boolean success = false; 
		try {
			fileWriter = new FileWriter(fileName);

			if (fileWriter != null) {
				fileWriter.write(contents);
				fileWriter.flush();
				fileWriter.close();
				success = true; 
			}

			
		} catch (FileNotFoundException e1) {
			Log.e(LOG_TAG, "File not found " + fileName + " \n" + e1.getMessage());
			e1.printStackTrace();


		} catch (IOException ioe) {
			Log.e(LOG_TAG, "IOException while writing to file -> " + fileName + " \n" + ioe.getMessage());
			ioe.printStackTrace();
		}
		
		return success; 
	}

}

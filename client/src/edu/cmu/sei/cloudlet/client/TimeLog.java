package edu.cmu.sei.cloudlet.client;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import android.os.Environment;
import android.util.Log;

/**
 * Helps storing time information in a log. Useful for performance tests.
 * @author secheverria copied over from dominik's class.
 *
 */
public class TimeLog 
{
    // For Android logging.
	private final static String LOG_TAG = TimeLog.class.getName();
	
	// Folder for logs.
    static final String LOG_FOLDER = Environment.getExternalStorageDirectory()
            .getAbsolutePath() + "/cloudlet/logs/";	
	
	// A map of timestamps and nametags of events.
	private static List<Long> stampTimes = new ArrayList<Long>();
	private static List<String> stampTexts = new ArrayList<String>();
	
	// Stores the last stamp to easily calculate diff with previous stamp.
	private static long lastStamp = 0;

	/**
	 * Adds a new "stamp" to the in-memory log.
	 * @param tag a string to give a name to this timestamp, usually an event.
	 */
	public static void stamp(String tag) 
	{
		// Get the current time.
		long time = System.currentTimeMillis();

		// Only when initializing, set the last stamp to the current time.
		if(lastStamp == 0)
		{
			lastStamp = time;
		}
		
		// Calculate the diff from the last one.
		long diffFromLast = time - lastStamp;
		
		// Log the stamp
		stampTimes.add(Long.valueOf(time));
		stampTexts.add(tag);
		Log.d(LOG_TAG, "@" + time + " (+" + diffFromLast  + " ms) " + tag);
		
		// Update the last time with the current one.
		lastStamp = time;
	}

	/**
	 * Write the whole log to a file.
	 * @param file
	 * @throws IOException
	 */
	public static void writeToFile(String file) throws IOException 
	{
	    // Create the folder if it is not there.
	    new File(LOG_FOLDER).mkdirs();	    
	    
        Log.d(LOG_TAG, "Write TimeLog to " + file);

        // Prepare a file and the end-of-line symbol.
		FileWriter writer = new FileWriter(LOG_FOLDER + "/" + file);
        String eol = System.getProperty("line.separator");
        
		writer.write("TIMELOG " + file + eol);
		
		// Write the timestamps, events and differences from beginning.
		if(stampTimes.size() > 0)
		{
    		long initialTimeStamp = stampTimes.get(0);
    		long previousTimeStamp = stampTimes.get(0);
    		for (int i=0; i<stampTimes.size(); i++) 
    		{
    		    long currentTimeStamp = stampTimes.get(i);
    			String tag = stampTexts.get(i);
                long diffFromStart = currentTimeStamp - initialTimeStamp;	
                long diffFromPrevious = currentTimeStamp - previousTimeStamp;
    			writer.write(String.format("%d (+%d ms): %s (+%d ms)%s", currentTimeStamp, diffFromPrevious, tag, diffFromStart, eol));
    			
    			previousTimeStamp = currentTimeStamp;
    		}
		}
		
		writer.close();
	}

	/**
	 * Remove all timestamps from memory.
	 */
	public static void reset() 
	{
	    lastStamp = 0;
	    stampTimes.clear();
	    stampTexts.clear();
	}
}

#!/usr/bin/env python
#       

# For time management.
import time
import datetime

# For path management.
import os.path

# To create folders.
import os

################################################################################################################
# Helps storing time information in a log. Useful for performance tests.
################################################################################################################
class TimeLog(object): 
    
    # Folder where apps to be pushed are stored.
    LOG_FOLDER = os.path.join(os.path.abspath(os.getcwd()), "logs")    
    
    # A map of timestamps and nametags of events.
    _stamps = {}
    
    # Stores the last stamp to easily calculate diff with previous stamp.
    _lastStamp = 0;

    ################################################################################################################
    # Adds a new "stamp" to the in-memory log.
    # @param tag a string to give a name to this timestamp, usually an event.
    ################################################################################################################
    @staticmethod
    def stamp(tag):     
        # Get the current time.
        currTime = time.time()

        # Only when initializing, set the last stamp to the current time.
        if(TimeLog._lastStamp == 0):
            TimeLog._lastStamp = currTime;
        
        # Log the stamp
        TimeLog._stamps[currTime] = tag;
        print tag + " (logged)"
        
        # Update the last time with the current one.
        TimeLog._lastStamp = currTime;

    ################################################################################################################
    # Write the whole log to a file.
    # @param file the filename for the log.
    ################################################################################################################
    @staticmethod
    def writeToFile(logFilename='vmlog.txt'): 
        # Create the folder if it doesn't exist.
        if(not os.path.exists(TimeLog.LOG_FOLDER)):
            os.makedirs(TimeLog.LOG_FOLDER)
        
        # Create and open the file to write the stamps to.
        localFilePath = os.path.join(TimeLog.LOG_FOLDER, logFilename)
        with open(localFilePath, "a") as completeLocalFile: 
            # Write a header to the file.   
            completeLocalFile.write("TIMELOG " + logFilename + '\n')
            
            # Get the timestamps as a sorted dictionary, to write things in chronological order.
            sortedStamps = sorted(TimeLog._stamps)            
            initialTimestamp = sortedStamps[0]
            previousTimestamp = initialTimestamp 
            for currentTimestamp in sortedStamps:
                # Calculate the time transcurred between events.
                tag = TimeLog._stamps[currentTimestamp]
                diffFromStart = 1000*(currentTimestamp - initialTimestamp)
                diffFromPrevious = 1000*(currentTimestamp - previousTimestamp)
                
                # Write to file.
                eventTime = datetime.datetime.fromtimestamp(currentTimestamp).strftime("%H:%M:%S.%f")
                completeLocalFile.write("%s (+%d ms): %s (+%d ms)\n" % (eventTime, diffFromPrevious, tag, diffFromStart))
                
                # Update the previous stanp variable for the next iteration.
                previousTimestamp = currentTimestamp
        
    ################################################################################################################
    # Remove all timestamps from memory.
    ################################################################################################################
    @staticmethod
    def reset():
        TimeLog._lastStamp = 0
        TimeLog._stamps.clear()

################################################################################################################
# Command line test
################################################################################################################
def testTimelog():  
    TimeLog.stamp('Starting test...')

    TimeLog.stamp('Waiting for a second...')
    time.sleep(1)
    TimeLog.stamp('Stopped waiting.')
    
    TimeLog.stamp('Waiting for 2 seconds...')
    time.sleep(2)
    TimeLog.stamp('Stopped waiting.') 
    
    TimeLog.stamp('Writing to file...')
    TimeLog.writeToFile('testlog.txt')   
    
    TimeLog.stamp('Process finished')


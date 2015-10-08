#!/bin/bash
# Source: https://stackoverflow.com/questions/4672383/how-to-run-cronjobs-more-often-than-once-per-minute/17132983#17132983

inputPeriod=$1
runCommand=$2
RUN_TIME=60
error="no"

if [ 'x'"$runCommand" != 'x' ]
then
    if [ 'x'$inputPeriod != 'x' ]
    then
        loops=$(( $RUN_TIME / $inputPeriod ))
        if [ $loops -eq 0 ]
        then
            loops=1
        fi

        for i in $(eval echo {1..$loops})
        do
            $runCommand
            sleep $inputPeriod
        done

    else
        error="yes"
    fi
else
    error="yes"
fi

if [ $error = "yes" ]
then
    echo "runEvery - runs a command every X seconds for a minute"
    echo "Usage: runEvery.sh <# in seconds < 60> <command to run>"
fi

#!/bin/sh
cd /home/cloudlet/FaceRecognitionServer
LD_LIBRARY_PATH=`pwd`/lib ./FaceRec name_map.txt

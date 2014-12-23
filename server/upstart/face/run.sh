#!/bin/sh
cd /home/cloudlet/face_server
LD_LIBRARY_PATH=`pwd`/lib ./FaceRec name_map.txt

#!/bin/bash

NAME=$1
FOLDER=$2

mkdir -p $FOLDER

(umask 277 && certtool --generate-privkey > $FOLDER/$NAME.key.pem)

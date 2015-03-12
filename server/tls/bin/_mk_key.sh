#!/bin/bash

NAME=$1
FOLDER=$2

(umask 277 && certtool --generate-privkey > $FOLDER/$NAME.key.pem)

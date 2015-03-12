#!/bin/bash

NAME=$1

(umask 277 && certtool --generate-privkey > $NAME.key.pem)

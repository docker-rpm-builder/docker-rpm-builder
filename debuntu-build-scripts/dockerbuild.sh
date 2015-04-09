#!/bin/bash
set -e
[ -n "$1" ] # target image
[ -n "$2" ] # script to run

docker run -v $(pwd):/host "$1" "/host/$2"

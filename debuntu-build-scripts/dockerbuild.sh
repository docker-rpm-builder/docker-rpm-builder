#!/bin/bash
set -e

docker run -v $(pwd):/host "$@"

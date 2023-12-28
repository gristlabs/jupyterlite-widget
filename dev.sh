#!/usr/bin/env bash

set -eux

npm run clean
jupyter labextension develop ./extension
./package.sh
jupyter lite serve

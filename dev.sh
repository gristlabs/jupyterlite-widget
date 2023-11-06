#!/usr/bin/env bash

set -eux

rm -rf _output .jupyterlite.doit.db
jupyter labextension develop ./extension
./package.sh
jupyter lite serve

#!/usr/bin/env bash

set -e

echo Current Working Dir: "$PWD"

if [ ! -e "src/slambda/data/playground.frontend" ]; then
    echo "playground.frontend does not exist."
    echo "build playground frontend first. i.e. make playground"
    exit 1
fi

python3 -m build
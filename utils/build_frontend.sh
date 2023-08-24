#!/usr/bin/env bash

set -e

echo Current Working Dir: "$PWD"

cd slambda-playground
npm run build
zip frontend.zip -r build
mv frontend.zip playground.frontend
cd ..
mkdir -p src/slambda/data
cp slambda-playground/playground.frontend src/slambda/data/playground.frontend
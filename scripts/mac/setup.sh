#!/bin/bash

cd ../..

#
# CLI.
# The CLI is where the neural network is located.
#
# Requirements:
# * Python3 and pip3 (I use 3.6.8)
# * CUDA 10.0
#

# PyInstaller will allow us to compile and package everything in a simple binary
pip3 --no-cache-dir install pyinstaller

# This command should resolve and install all the necessary packages
pip3 --no-cache-dir install -r requirements-ubuntu.txt

# NOTES from wisp101:
# Make sure pyinstaller is accessible from the cmdline as "pyinstaller".
# Otherwise, track down its folder and add it to your path. I found mine in "~/.local/bin".

#
# Success
#

echo "Installation completed!"
echo "- Now you can run the build.bat script to compile the project and get an easy-to-use binary"
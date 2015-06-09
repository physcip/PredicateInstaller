#!/bin/bash

# Software Update Tool
# Copyright 2002-2012 Apple Inc.
# 
# Finding available software
# Software Update found the following new or updated software:
#    * 031-4751-5.1.0.0
# 	Command Line Developer Tools for OS X Mavericks (5.1.0.0), 122107K [recommended]


touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress

pkgname=$(softwareupdate --list | grep -A 1 '*' | grep -B 1 'Command Line' | head -n 1 | awk '{print $2}')

softwareupdate --install $pkgname
result=$?

rm /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress

exit $result

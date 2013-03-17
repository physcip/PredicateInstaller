#!/bin/bash

# Software Update Tool
# Copyright 2002-2010 Apple
# 
# Software Update found the following new or updated software:
#    * JavaForOSX-1.0
#         Java for OS X 2013-002 (1.0), 65039K [recommended]


export JAVA_INSTALL_ON_DEMAND=1

pkgname=$(softwareupdate --list | grep '*' | grep -i java | awk '{print $2}')

softwareupdate --install $pkgname

exit $?

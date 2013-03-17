#!/usr/bin/python

import subprocess
import os

pkgs = [
	'"com.apple.java.runtime" IN tags'
]

os.environ['JAVA_INSTALL_ON_DEMAND'] = '1'

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py'), pkg])

#!/usr/bin/python

import subprocess
import os

pkgs = [
	'"BootCampAutoUnattend" IN tags'
]

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py'), pkg])

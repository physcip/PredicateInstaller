import subprocess
import os

pkgs = [
	'"com.apple.java.runtime" IN tags'
]

os.environ['JAVA_INSTALL_ON_DEMAND'] = '1'

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', 'predicate_installer.py', pkg])

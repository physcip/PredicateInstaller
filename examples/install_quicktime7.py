import subprocess
import os

pkgs = [
	'"QuickTimePlayerLegacyContentHandler" IN tags'
]
# On Mountain Lion, this actually installs a version that's newer (Version 7.6.6 (1710)) than the one downloadable at Apple (Version 7.6.6 (1709)).

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', 'predicate_installer.py', pkg])

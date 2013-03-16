import subprocess
import os

pkgs = [
	'"VOICEID:com.apple.speech.synthesis.voice.anna.premium_2" IN tags',
	'"VOICEID:com.apple.speech.synthesis.voice.steffi.premium_2" IN tags',
	'"VOICEID:com.apple.speech.synthesis.voice.yannick.premium_2" IN tags'
]

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', 'predicate_installer.py', pkg])

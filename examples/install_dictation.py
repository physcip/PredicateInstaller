#!/usr/bin/python

import subprocess
import os
import platform

if int(platform.release().split('.')[0]) < 13: # Mavericks
        raise Exception("Dictation is not available in OS X below 10.9")

pkgs = [
	'"SRCLANGID:com.apple.speech.SpeechRecognitionCoreLangauge.en_US" IN tags',
	'"SRCLANGID:com.apple.speech.SpeechRecognitionCoreLangauge.de_DE" IN tags'
]

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py'), pkg])

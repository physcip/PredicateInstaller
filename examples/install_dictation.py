#!/usr/bin/python

import subprocess
import os
import platform

num = int(platform.release().split('.')[0])-12 # 13=>1: Mavericks
if num == 3 or num == 4:
	num = 2
elif num >= 5:
	num -= 3
if num <= 0:
	raise Exception("Dictation is not available in OS X below 10.9")
if num == 1:
	num = ''
else:
	num = '_%d' % num

pkgs = [
	'"SRCLANGID:com.apple.speech.SpeechRecognitionCoreLanguage.en_US%s" IN tags' % num,
	'"SRCLANGID:com.apple.speech.SpeechRecognitionCoreLanguage.de_DE%s" IN tags' % num
]
if num == 1: # fix a typo in Mavericks
	for i in range(len(pkgs)):
		pkgs[i] = pkgs[i].replace('Language','Langauge')

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py'), pkg])

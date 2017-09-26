#!/usr/bin/python

import subprocess
import os
import platform

num = int(platform.release().split('.')[0])-10 # 13=>3: Mavericks, 12=>2: Mountain Lion, 11=>1: Lion
if num >= 7:
	num -= 1
if num <= 0:
	raise Exception("Voices are not available in OS X below 10.7")
if num == 1:
	num = ''
else:
	num = '_%d' % num

pkgs = [
	'"VOICEID:com.apple.speech.synthesis.voice.anna.premium%s" IN tags' % num,
	'"VOICEID:com.apple.speech.synthesis.voice.yannick.premium%s" IN tags' % num
]

if num < 3:
	pkgs.append('"VOICEID:com.apple.speech.synthesis.voice.steffi.premium%s" IN tags' % num)
if num >= 3:
	pkgs.append('"VOICEID:com.apple.speech.synthesis.voice.markus.premium%s" IN tags' % num)
	pkgs.append('"VOICEID:com.apple.speech.synthesis.voice.petra.premium%s" IN tags' % num)

for pkg in pkgs:
	subprocess.call(['/usr/bin/python', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py'), pkg])

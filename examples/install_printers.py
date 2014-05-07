#!/usr/bin/python

import subprocess
import os
from install_printers_config import printers

predicate_installer = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predicate_installer.py') # in this directory
if not os.path.exists(predicate_installer):
	predicate_installer = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py') # in parent directory

# restart CUPS and make sure it's running
subprocess.call(['/bin/launchctl', 'unload', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])
subprocess.call(['/bin/launchctl', 'load', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])
subprocess.check_call(['/bin/launchctl', 'start', 'org.cups.cupsd'])

for printer in printers:
	try:
		if 'ppd' in printer and not os.path.exists(printer['ppd']) and 'predicate' in printer:
			# mark printer as connected
			subprocess.check_call(['/usr/libexec/PlistBuddy', '-c', "Add InstalledPrinters: string " + printer['model'], '/Library/Printers/InstalledPrinters.plist'])
			# install printer driver
			subprocess.call(['/usr/bin/python', predicate_installer, printer['predicate']])
		elif 'ppd' in printer and 'download' in printer:
			from distutils.version import StrictVersion
			try:
				if not os.path.exists(printer['ppd']):
					raise Exception()
				installed_version = subprocess.check_output(['/usr/bin/zgrep', '^*FileVersion:', printer['ppd']]).split(':')[1].strip().replace('"','').replace("'",'')
			except:
				installed_version = '0.0'
			if not 'version' in printer:
				printer['version'] = '0.0'
			if not os.path.exists(printer['ppd']) or StrictVersion(printer['version']) > StrictVersion(installed_version):
				dmg = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(printer['download']))
				subprocess.check_call(['/usr/bin/curl', '-L', '-o', dmg, printer['download']])
				mount = subprocess.check_output(['/usr/bin/hdiutil', 'attach', '-plist', dmg]).split('\n')
				mountpoint = None
				for i in range(len(mount)):
					if 'mount-point' in mount[i]:
						mountpoint = mount[i+1].strip().replace('<string>','').replace('</string>','')
						break
				if mountpoint is None:
					raise Exception('Could not mount DMG')
				pkgpath = os.path.join(mountpoint, printer['pkgpath'])
				print "Installing %s" % pkgpath
				subprocess.check_call(['/usr/sbin/installer', '-package', pkgpath, '-target', '/'])
				subprocess.check_call(['/usr/bin/hdiutil', 'detach', mountpoint])
		elif 'ppd' not in printer and 'download' in printer and printer['download'].endswith('.ppd'):
			printer['ppd'] = os.path.join('/usr/share/cups/model', os.path.basename(printer['download']))
			print "Downloading %s" % os.path.basename(printer['ppd'])
			subprocess.check_call(['/usr/bin/curl', '-L', '-o', printer['ppd'], printer['download']])
		if not os.path.exists(printer['ppd']):
			raise Exception('PPD not found')
		if printer['ppd'].startswith('/usr/share/cups/model'):
			printer['ppd'] = os.path.basename(printer['ppd']) # relative path required
		
		# delete print queue if it already exists
		DEVNULL = open(os.devnull, 'w')
		if subprocess.call(['/usr/bin/lpstat', '-p', printer['name']], stdout=DEVNULL, stderr=DEVNULL) == 0: # printer exists
			subprocess.call(['/usr/sbin/lpadmin', '-x', printer['name']])
		DEVNULL.close()
		
		# add print queue
		subprocess.check_call(['/usr/sbin/lpadmin', '-p', printer['name'], '-v', printer['uri'], '-m', printer['ppd'], '-L', printer['location'], '-E', '-o', 'printer-is-shared=false'])
		
		# set printer options
		if 'options' in printer and len(printer['options']) > 0:
			optionstrings = []
			for k,v in printer['options'].iteritems():
				optionstrings.append('-o')
				optionstrings.append('%s=%s' % (k,v))
		
			subprocess.check_call(['/usr/sbin/lpadmin', '-p', printer['name']] + optionstrings)
		
	except Exception as e:
		print "Could not add printer %s: %s" % (printer['name'], e)

subprocess.check_call(['/bin/launchctl', 'unload', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])
with open('/etc/cups/printers.conf') as f:
	pr = f.readlines()
	
for printer in printers:
	cache_dirty = False
	ppd_path = os.path.join('/etc/cups/ppd', printer['name'] + '.ppd')
	if 'remote' in printer and printer['remote'] == True:
		section = False
		for i,line in enumerate(pr):
			if line.startswith('<Printer ' + printer['name'] + '>'):
				section = True
			elif line.startswith('</Printer>'):
				section = False
			
			# set CUPS_PRINTER_REMOTE in Type
			if section and line.startswith('Type '):
				pr[i] = 'Type %d\n' % (int(line[5:-1]) | 2)
		
		# process the job on the server instead of on the client
		f_ppd = open(ppd_path, 'a')
		f_ppd.write('\n\n')
		for mimetype in ["application/pdf", "image/*", "application/postscript", "application/vnd.cups-postscript", "application/vnd.cups-command"]:
			f_ppd.write('*cupsFilter: "%s 0 -"\n' % mimetype)
		f_ppd.close()
		cache_dirty = True
		
	if 'editppd' in printer:
		import re
		f_ppd = open(ppd_path, 'r+')
		ppd = f_ppd.read()
		for o,n in printer['editppd'].iteritems():
			ppd = re.sub(o,n, ppd)
		f_ppd.seek(0)
		f_ppd.write(ppd)
		f_ppd.close()
		cache_dirty = True
	
	if cache_dirty: # need to delete the PPD cache. OS X 10.8 appears to have done that automatically, but 10.9 keeps using the old cupsFilter list if we don't do this
		os.unlink('/var/spool/cups/cache/' + printer['name'] + '.data')

with open('/etc/cups/printers.conf', 'w') as f:
	f.writelines(pr)
subprocess.check_call(['/bin/launchctl', 'load', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])

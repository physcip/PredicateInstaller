#!/usr/bin/python

import subprocess
import os
import platform

darwin = int(platform.release().split('.')[0])

printers = []
printers.append({
	'predicate' : '("printing software" IN tags OR "printer update" IN tags) AND "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520" IN tags',
	'model' : "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520",
	'uri' : 'ipp://robert.physcip.uni-stuttgart.de:631/printers/ghost_physcip_uni_stuttgart_de',
	'ppd' : '/Library/Printers/PPDs/Contents/Resources/HP Color LaserJet CP4020 CP4520 Series.gz',
	'name' : 'ghost',
	'location': 'CIP Pool Physik',
	'options' : {
		'InstalledMemory' : '1048576',
		'OptionalTray' : 'HP3x500PaperFeeder',
		'HPOption_Duplexer' : 'True',
		'HPOption_Disk' : 'True',
		'PageSize' : 'A4',
		'Duplex' : 'DuplexNoTumble',
		'HPBookletPageSize' : 'A4',
	},
	'remote' : True,
})
printers.append({
	'uri' : 'ipp://robert.physcip.uni-stuttgart.de:631/printers/nymeria_physcip_uni_stuttgart_de',
	'ppd' : '/Library/Printers/PPDs/Contents/Resources/KONICAMINOLTAC454e.gz',
	'name' : 'nymeria',
	'location': 'CIP Pool Physik',
	'options' : {
		'PaperSources' : 'PC410',
		'Finisher' : 'FS533',
		'KMPunchUnit' : 'PK519-EU4',
		'SelectColor' : 'Grayscale',
		#'ColorModel' : 'Gray',
		#'SimulationProfile' : 'None',
	},
	'remote' : True,
})
if darwin == 10:
	printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=DL/201307/25042126/BHC554ePSMacOS106_302MU.dmg'
	printers[-1]['version'] = '3.0.2'
	printers[-1]['pkgpath'] = 'A4/bizhub_C554_106.pkg'
elif darwin == 11:
	printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=DL/201307/25042758/BHC554ePSMacOS107_302MU.dmg'
	printers[-1]['version'] = '3.0.2'
	printers[-1]['pkgpath'] = 'A4/bizhub_C554_107.pkg'
elif darwin == 12:
	printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=DL/201307/25043316/BHC554ePSMacOS108_302MU.dmg'
	printers[-1]['version'] = '3.0.2'
	printers[-1]['pkgpath'] = 'A4/bizhub_C554_108.pkg'
elif darwin == 13:
	printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=dl/201401/13110019/bizhub_C554e_109.dmg'
	printers[-1]['version'] = '4.5.3'
	printers[-1]['pkgpath'] = 'bizhub_C554_C364_109.pkg'

# To figure out the model, run /System/Library/SystemConfiguration/PrinterNotifications.bundle/Contents/MacOS/makequeues with the -q flag (on OS X 10.6) or -B flag (on OS X 10.8), which performs a Bonjour scan. 
# To figure out available options, run lpoptions -d printername -l after you initially added the printer

predicate_installer = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predicate_installer.py') # in this directory
if not os.path.exists(predicate_installer):
	predicate_installer = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py') # in parent directory

# restart CUPS and make sure it's running
subprocess.call(['/bin/launchctl', 'unload', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])
subprocess.call(['/bin/launchctl', 'load', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])
subprocess.check_call(['/bin/launchctl', 'start', 'org.cups.cupsd'])

for printer in printers:
	try:
		if not os.path.exists(printer['ppd']) and 'predicate' in printer:
			# mark printer as connected
			subprocess.check_call(['/usr/libexec/PlistBuddy', '-c', "Add InstalledPrinters: string " + printer['model'], '/Library/Printers/InstalledPrinters.plist'])
			# install printer driver
			subprocess.call(['/usr/bin/python', predicate_installer, printer['predicate']])
		elif 'download' in printer:
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
		if not os.path.exists(printer['ppd']):
			raise Exception('PPD not found')
		
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

with open('/etc/cups/printers.conf', 'w') as f:
	f.writelines(pr)
subprocess.check_call(['/bin/launchctl', 'load', '/System/Library/LaunchDaemons/org.cups.cupsd.plist'])

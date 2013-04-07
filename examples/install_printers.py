#!/usr/bin/python

import subprocess
import os

printers = []
printers.append({
	'predicate' : '("printing software" IN tags OR "printer update" IN tags) AND "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520" IN tags',
	'model' : "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520",
	'uri' : 'ipp://purple.physcip.uni-stuttgart.de:631/printers/ghost_physcip_uni_stuttgart_de',
	'ppd' : '/Library/Printers/PPDs/Contents/Resources/HP Color LaserJet CP4020 CP4520 Series.gz',
	'name' : 'ghost',
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

# To figure out the model, run /System/Library/SystemConfiguration/PrinterNotifications.bundle/Contents/MacOS/makequeues -q, which performs a Bonjour scan. 
# To figure out available options, run lpoptions -d printername -l after you initially added the printer

predicate_installer = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predicate_installer.py') # in this directory
if not os.path.exists(predicate_installer):
	predicate_installer = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'predicate_installer.py') # in parent directory

for printer in printers:
	try:
		if not os.path.exists(printer['ppd']):
			# mark printer as connected
			subprocess.check_call(['/usr/libexec/PlistBuddy', '-c', "Add InstalledPrinters: string " + printer['model'], '/Library/Printers/InstalledPrinters.plist'])
			# install printer driver
			subprocess.call(['/usr/bin/python', predicate_installer, printer['predicate']])
		if not os.path.exists(printer['ppd']):
			raise Exception('PPD not found')
		
		# delete print queue if it already exists
		DEVNULL = open(os.devnull, 'w')
		if subprocess.call(['/usr/bin/lpstat', '-p', printer['name']], stdout=DEVNULL, stderr=DEVNULL) == 0: # printer exists
			subprocess.call(['/usr/sbin/lpadmin', '-x', printer['name']])
		DEVNULL.close()
		
		# add print queue
		subprocess.check_call(['/System/Library/SystemConfiguration/PrinterNotifications.bundle/Contents/MacOS/makequeues', '-v', printer['uri'], '-d', printer['ppd'], '-q', printer['name']])
		
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

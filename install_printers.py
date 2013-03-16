#!/usr/bin/python

import subprocess
import os

printers = []
printers.append({
	'predicate' : '("printing software" IN tags OR "printer update" IN tags) AND "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520" IN tags',
	'uri' : 'ipp://purple.physcip.uni-stuttgart.de:631/printers/wario.physcip.uni-stuttgart.de',
	'ppd' : '/Library/Printers/PPDs/Contents/Resources/HP Color LaserJet CP4020 CP4520 Series.gz',
	'name' : 'wario'
})

for printer in printers:
	try:
		if not os.path.exists(printer['ppd']):
			# install printer driver
			subprocess.call(['/usr/bin/python', 'predicate_installer.py', printer['predicate']])
		if not os.path.exists(printer['ppd']):
			raise Exception('PPD not found')
		
		# add print queue
		subprocess.call(['/System/Library/SystemConfiguration/PrinterNotifications.bundle/Contents/MacOS/makequeues', '-v', printer['uri'], '-d', printer['ppd'], '-q', printer['name']])
		
	except Exception as e:
		print "Could not add printer %s: %s" % (printer['name'], e)

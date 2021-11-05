import platform
import os

darwin = int(platform.release().split('.')[0])

printers = []

printers.append({
	'predicate' : '("printing software" IN tags OR "printer update" IN tags) AND "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520" IN tags',
	'model' : "MANUFACTURER:HP;MODEL:Color LaserJet CP4020-CP4520",
	'uri' : 'ipp://cups.physcip.uni-stuttgart.de:631/printers/ghost',
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
	'uri' : 'ipp://cups.physcip.uni-stuttgart.de:631/printers/nymeria',
	'name' : 'nymeria',
	'location': 'CIP Pool Physik',
	'options' : {
		'PaperSources' : 'PC416',
		'Finisher' : 'FS533',
		'KOPunch' : 'PK519-4',
		'SelectColor' : 'Grayscale',
		'KMDuplex' : '2Sided',
		'PageSize' : 'A4',
	},
	'remote' : True,
	'download' : 'http://cups.physcip.uni-stuttgart.de:631/printers/nymeria.ppd',
	'download_icon' : 'http://cups.physcip.uni-stuttgart.de:631/icons/nymeria.png',
})

# if darwin == 10:
#     printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=DL/201307/25042126/BHC554ePSMacOS106_302MU.dmg'
#     printers[-1]['version'] = '3.0.2'
#     printers[-1]['pkgpath'] = 'A4/bizhub_C554_106.pkg'
# elif darwin == 11:
#     printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=DL/201307/25042758/BHC554ePSMacOS107_302MU.dmg'
#     printers[-1]['version'] = '3.0.2'
#     printers[-1]['pkgpath'] = 'A4/bizhub_C554_107.pkg'
# elif darwin == 12:
#     printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=DL/201307/25043316/BHC554ePSMacOS108_302MU.dmg'
#     printers[-1]['version'] = '3.0.2'
#     printers[-1]['pkgpath'] = 'A4/bizhub_C554_108.pkg'
# elif darwin == 13:
#     printers[-1]['download'] = 'https://o.cses.konicaminolta.com/file/Default.aspx?FilePath=dl/201401/13110019/bizhub_C554e_109.dmg'
#     printers[-1]['version'] = '4.5.3'
#     printers[-1]['pkgpath'] = 'bizhub_C554_C364_109.pkg'

# To figure out the model, run /System/Library/SystemConfiguration/PrinterNotifications.bundle/Contents/MacOS/makequeues with the -q flag (on OS X 10.6) or -B flag (on OS X 10.8), which performs a Bonjour scan. 
# To figure out available options, run lpoptions -d printername -l after you initially added the printer

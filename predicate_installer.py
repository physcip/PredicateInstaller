#!/usr/bin/python

import objc
from Cocoa import NSPredicate, NSObject
import time
import os
import sys
from threading import Thread
from PyObjCTools import AppHelper

def installlog():
	f = open('/var/log/install.log', 'r')
	f.seek(0, os.SEEK_END)
	while installlog_stop == False:
		line = f.readline()
		if len(line) == 0:
			time.sleep(1)
		else:
			print line,
	f.close()

# follow log file
installlog_stop = False
installlog_thread = Thread(target=installlog)
installlog_thread.daemon = True
installlog_thread.start()

os.environ['COMMAND_LINE_INSTALL'] = "1"

# load private framework
framework="/System/Library/PrivateFrameworks/SoftwareUpdate.framework"
objc.loadBundle("SoftwareUpdate", globals(), framework)

# set up predicate
if len(sys.argv) < 2:
	raise Exception('Please specify a predicate on the command line')
predicate = sys.argv[1]
predicate = NSPredicate.predicateWithFormat_(predicate)

# set up scanner
scan = SUScan.alloc().init()
scan.setDistributionPredicate_(predicate)

# start scanning
scan.performSynchronousScan()

#scan.start()
#while scan.isExecuting() == 1 and scan.isFinished() != 1:
#	print "Executing: %s" % (scan.isExecuting(), scan.isFinished())
#	time.sleep(2)

if scan.error() is not None:
	raise Exception("Scan failed: %s" % scan.error())
products = scan.installableProducts()
if len(products) < 1:
	raise Exception("No products found")

for product in products:
	 print "Installing", product.displayName(), product.displayVersion(), product.productKey(), ", ".join(product.packageIdentifiersToInstall())

class SessionDelegate(NSObject):
	session = None

	#def session_willEnd_(arg1, arg2, sender):
	def session_willEnd_(self, arg1, arg2):
		print "session %s. willEnd: %s" % (arg1, arg2)
		session = arg1
	
	#def sessionDidBegin_(arg1, sender):
	def sessionDidBegin_(self, arg1):
		print "session %s did begin" % (arg1)
		pass

delegate = SessionDelegate.alloc().init()
if hasattr(SUSession, 'initWithProducts_options_delegate_'): # Mac OS X 10.8
	session = SUSession.alloc().initWithProducts_options_delegate_(products, 0, delegate)
elif hasattr(SUSession, 'initWithProducts_downloadDirectory_options_delegate_'): # Mac OS X 10.6
	session = SUSession.alloc().initWithProducts_downloadDirectory_options_delegate_(products, '/Library/Updates', 0, delegate)
else:
	raise Exception("SUSession.initWithProducts_ not found")
session.start()
AppHelper.runConsoleEventLoop(installInterrupt=True)
#while True:
#	print session.doesInstall(), session.didFail(), session.sessionDidBegin()
#	print session._estimatedTimeRemainingForCurrentState(), session._currentAverageBytesPerSecond()
#	time.sleep(2)

#sessionimpl = SUSessionImpl.alloc().init()
#sessionimpl.installAllProductsSync_(products)
#while True:
#	time.sleep(2)
#if sessionimpl.didFail() != 0:
#	raise Exception("Installation failed: %s" % sessionimpl.combinedErrorMessage())

time.sleep(2)
installlog_stop = True
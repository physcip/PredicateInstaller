#!/usr/bin/python

import objc
from Cocoa import NSPredicate, NSObject
import time
import os
import sys
import platform
import subprocess
from threading import Thread
from PyObjCTools import AppHelper

metaFile = "/Library/Updates/ProductMetadata.plist"

if (not os.path.isfile(metaFile) or os.path.getsize(metaFile) < 2**10): #1KB
	subprocess.check_call(['/usr/sbin/softwareupdate', "--list"])

finishedInstall = False

def installlog():
	f = open('/var/log/install.log', 'r')
	f.seek(0, os.SEEK_END)
	while installlog_stop == False:
		line = f.readline()
		if len(line) == 0:
			time.sleep(1)
		else:
			print line,
			if 'SoftwareUpdate: finished install' in line:
				global finishedInstall
				finishedInstall = True
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

if int(platform.release().split('.')[0]) >= 13: # OS X 10.9 and higher
	
	class ControllerDelegate(NSObject):
		def __getattr__(self, name):
			def method(*args):
				print("tried to handle unknown method " + name)
				if args:
					print("it had arguments: " + str(args))
				return True
			return method
	
	controller = SUSoftwareUpdateController.alloc().initWithDelegate_localizedProductName_(ControllerDelegate, "SU Predicate")
	if controller.countOfCachedProductsMatchingPredicate_(predicate) == 0:
		raise Exception("No products found for %s" % sys.argv[1])
	
	md = controller.metadataOfCachedProductsMatchingPredicate_(predicate)
	#print md
	
	# get matching product keys
	mdcache = SUMetadataCache.alloc().init()
	productkeys = mdcache.cachedProductKeysMatchingPredicate_(predicate)
	#print productkeys
	
	conn = objc.getInstanceVariable(controller, '_connection')
	serviceclient = conn.remoteObjectProxy()
	serviceclient.dumpServiceDebugInfo()
	
	controller.startUpdateInBackgroundWithPredicate_(predicate)
	
	startedInstall = False
	while True:
		# _runningUpdate is the only thing that ever changes. currentState is always zero. 
		# unfortunately getting a struct from PyObjC always logs a warning
		
		runningUpdate = objc.getInstanceVariable(controller, '_runningUpdate')
		if not startedInstall and runningUpdate != None:
			startedInstall = True
		elif startedInstall and runningUpdate == None:
			break
		time.sleep(5)
	
	# SUUpdateServiceDaemon._installProducts, SUUpdateServiceDaemon.startUpdatesForProductKeys and SUUpdateSession.startUpdateForProducts cannot be used because they take an ObjC block as their final argument, which PyObjC doesn't yet appear to support.
	# SUUpdateSession._startTransactionForForeground doesn't work because we don't have a simple way to get product objects from product keys.

	sys.exit()

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
	raise Exception("No products found for %s" % sys.argv[1])

for product in products:
	 print "Installing", product.displayName().encode("ascii", "replace"), product.displayVersion(), product.productKey(), ", ".join(product.packageIdentifiersToInstall())

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

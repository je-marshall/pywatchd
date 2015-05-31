import os, sys, time, atexit
import md5
import ConfigParser
from daemon import Daemon
from signal import signal, SIGINT
from multiprocessing import Process
from optparse import OptionParser
from pyinotify import ProcessEvent, WatchManager, Notifier, IN_CREATE, IN_DELETE, IN_MODIFY, IN_MOVED_FROM, IN_MOVED_TO


class daemon_watch(Daemon):
	'''Subclass of Daemon class to enable the process to run in the
	background.'''

	def run(self):
		
		if not os.path.isdir(self.directory):
			sys.exit(1)

		self.w = dir_watch(self.directory)
	
		try:
			self.w.notifier.loop()	
		except:
			print "Exiting"

		atexit.register(self.w.write_list())


class dir_watch():
	'''This is the class that does the actual watching of a directory,
	as well as containing the functions for printing out a list of files
	that have been changed/modified'''

	def __init__(self, directory):
	
		self.directory = directory
		self.file_list = []
		self.wm = WatchManager()
		self.active = False

		mask = IN_CREATE | IN_DELETE | IN_MODIFY | IN_MOVED_FROM | IN_MOVED_TO
		
		self.tracking = tracker(file_list=self.file_list)
		self.notifier = Notifier(self.wm, default_proc_fun=self.tracking)

		watch = self.wm.add_watch(directory, mask, rec=True)


	def write_list(self):
		
		with open('%s/pywatchd_report.txt' % self.directory, 'w') as f:
			for i in self.file_list:
				f.write('%s\n' % i)


class tracker(ProcessEvent):
	'''This is the class that controls how events are processed and is
	meant to be called from within the dir_watch class. A list is passed
	to the class from the dir_watch class'''

	def my_init(self, file_list):

		self.file_list = file_list

	def process_IN_CREATE(self, event):
		# If file is not in list, add it	

		print "created: %s" % event.pathname
		if event.pathname not in self.file_list:
			if os.path.isfile(event.pathname):
				self.file_list.append(event.pathname)

	def process_IN_DELETE(self, event):
		# If file is in list, delete it

		print "deleted: %s" % event.pathname
		if event.pathname in self.file_list:
			self.file_list.remove(event.pathname)
	
	def process_IN_MODIFY(self, event):
		# If file is not in list, add it

		print "modified: %s" % event.pathname
		if event.pathname not in self.file_list:
			if os.path.isfile(event.pathname):
				self.file_list.append(event.pathname)

	def process_IN_MOVED_FROM(self, event):
		# If file is in list, delete it
		
		print "moved from: %s" % event.pathname
		if event.pathname in self.file_list:
			self.file_list.remove(event.pathname)

	def process_IN_MOVED_TO(self, event):
		# If file is not in list, add it	
		
		print "moved to: %s" % event.pathname
		if event.pathname not in self.file_list:
			if os.path.isfile(event.pathname):
				self.file_list.append(event.pathname)

def main():

	parser = OptionParser('''Call with directory to report about. Call can be start, stop or restart''')
	parser.add_option("-d", "--directory", nargs=1, dest='directory', help='''Directory to watch''')
	
	(options, args) = parser.parse_args()

	directory = options.directory

	if len(args) > 1:
		parser.error("Too many options specified")
	elif len(args) == 0:
		parse.error("Please specify an action")
	else:
		argument = args[0]

	
	if argument == 'start':
		dir_sum = md5.new(directory)
		pidfile = '/var/run/pywatchd/%s.pid' % dir_sum.hexdigest()
		daemon = daemon_watch(pidfile, directory)
		print "[INFO] Starting watch on %s" % directory
		daemon.start()
	elif argument == 'stop':
		dir_sum = md5.new(directory)
		pidfile = '/var/run/pywatchd/%s.pid' % dir_sum.hexdigest()
		daemon = daemon_watch(pidfile, directory)
		print "[INFO] Stopping watch on %s" % directory
		daemon.stop()
	elif argument == 'restart':
		dir_sum = md5.new(directory)
		pidfile = '/var/run/pywatchd/%s.pid' % dir_sum.hexdigest()
		daemon = daemon_watch(pidfile, directory)
		print "[INFO] Restarting watch on %s" % directory
		daemon.restart()
	else:
		parser.error("Try again")
		sys.exit(1)

if __name__ == '__main__':
	main()

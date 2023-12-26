import os
import sys
import signal
import subprocess as sh
from types import FrameType
from typing import Callable
from functools import partial

from CatalisUtils.logging import Logger
from CatalisUtils.database import CatalisDB, busy_handler

from time import strftime, gmtime
import apsw, apsw.bestpractice


# initialize apsw
apsw.bestpractice.apply((
	apsw.bestpractice.connection_busy_timeout,
	apsw.bestpractice.connection_enable_foreign_keys,
	apsw.bestpractice.connection_dqs
))


# daemon wrapper class
class DBDaemon():
	FSTYPE 			= os.environ.get("CATALIS_FSTYPE",					"vfat")
	LABEL_PREFIX 	= os.environ.get("CATALIS_LABEL_PREFIX", 			"DATA-HMI")
	DB_PATTERN 		= os.environ.get("CATALIS_DB_PATTERN", 				"polldata-hmi$HMID")
	BUSY_RETRY_INT 	= os.environ.get("CATALIS_DB_BUSY_RETRY_INTERVAL", 	"10")


	# constructor
	def __init__(self, name:str, prelim:Callable, main:Callable, cleanup:Callable, logger:Logger) -> None:
		self._name = name
		self._prelim = prelim
		self._main = main
		self._cleanup = cleanup
		self.logger = logger


	# startup + main loop
	def start(self) -> None:
		# write to journalctl log
		sh.run(f"echo 'Daemon starting - Logging to {self.logger}.'", shell=True)

		# register custom standard termination exit handler
		signal.signal(signal.SIGTERM, partial(self._exit_clean, self._cleanup))

		# get filesystem label and generate database path
		fs_label = sh.getoutput(f"lsblk -o label /dev/{sys.argv[1]} | tail -1")
		hmid = fs_label.strip(self.LABEL_PREFIX)
		dbpath = (f"/srv/CatalisDATA/database/{self.DB_PATTERN}.sqlite3").replace("$HMID", hmid)

		# print logging preamble
		self.logger.print(f"Catalis Cloud HMI {self._name} Daemon")
		self.logger.print(f"> Session date: {strftime('%F', gmtime())} (GMT)")
		self.logger.print(f"> CatKey label: {fs_label}")
		self.logger.print(f"> DB path: {dbpath}")

		# preliminary operations
		self._prelim()

		# initialize database connection
		self.logger.log("(init) <1/1> Connecting to database in Read-Write mode... ", endline=False)

		try:
			db = CatalisDB(dbpath, flags=apsw.SQLITE_OPEN_READWRITE, logger=self.logger)
			db._connection.set_busy_handler(partial(busy_handler, db._logger, int(self.BUSY_RETRY_INT)))
			self.logger.cap(f"connected to {dbpath}.")

		except apsw.CantOpenError as e: # fatally exit if unable to open in write mode
			self._exit_fatal(self.logger)

		# run main loop
		self._main(self, db)


	# cleanup + clean exit handler
	def _exit_clean(self, cleanup:Callable, signum:int, frame:FrameType) -> None:
		# run cleanup function
		cleanup() 

		# log clean exit
		self.logger.print(f"\nTerminated cleanly at {strftime('%T', gmtime())}.") # write to journalctl log
		sh.run(f"echo 'Daemon exiting cleanly.'", shell=True)

		sys.exit(0)


	# cleanup + fatal error exit handler
	def _exit_fatal(self, cleanup:Callable) -> None:
		cleanup()

		# log fatal exit
		self.logger.print(f"\nTerminated due to fatal error at {strftime('%T', gmtime())}.")
		sh.run(f"echo 'Daemon exiting with fatal error. Check log: {self.logger}'", shell=True) # write to journalctl log
		
		sys.exit(1)
from time import sleep

import apsw, apsw.bestpractice
from .logging import Logger

# initialize apsw
apsw.bestpractice.apply((
	apsw.bestpractice.connection_busy_timeout,
	apsw.bestpractice.connection_enable_foreign_keys,
	apsw.bestpractice.connection_dqs
))


# catalis polls sqlite database handler
class CatalisDB():
	def __init__(self, dbpath:str, flags:int=None, logger:Logger=None):
		self._logger = logger

		# try to connect to database
		try: 
			if flags: self._connection = apsw.Connection(dbpath, flags=flags)	
			else: self._connection = apsw.Connection(dbpath)	
		
		except apsw.CantOpenError as e: # failed to initialize database
			if self._logger:
				self._logger.cap("error.")
				self._logger.log(("Unable to open database file: check mountpoint "
							"exists + permissions (Sugg. fixes: Check mountpoint defined "
							"in /etc/catalis/global.conf and consult with your system "
							"administrator)."), level=Logger.FATAL)
				self._logger.log(e, level=Logger.TRACE)
			
			raise e


	# error-handling wrapper for execute
	def execute(self, query:str, bindings:tuple[str]=()) -> apsw.Cursor:
		try:
			return self._connection.execute(query, bindings)
		
		# failed to write to database
		except apsw.ReadOnlyError as e0:		
			if self._logger: 
				self._logger.cap("error.")
				self._logger.log(f"Failed while writing to database - ", level=Logger.FATAL, endline=False)
				
			try: # check if can open db, if yes assume permissions error
				test = apsw.Connection(self._connection.filename, flags=apsw.SQLITE_OPEN_READWRITE)
				
				if self._logger: 
					self._logger.log(("check mounted filesytem permissions (Sugg. "
				 				"fixes: Reinsert the storage volume to restart "
								"all services, or re-format drive and copy data back in)."))
					self._logger.log(e0, level=Logger.TRACE)
				
				raise e0
				
			except apsw.CantOpenError as e1: # otherwise, assume database deleted
				if self._logger: 
					self._logger.log(("local DB may have been deleted (Sugg. "
								"fixes: to prevent data loss - DO NOT UNPLUG "
								"USB KEY OR STOP/RESTART SERVICES UNTIL CLOUD "
								"SYNC SERVICE HAS FAILED)."))
					self._logger.log(e1, level=Logger.TRACE)
				
				raise e1


# sqlite db busy handler
def busy_handler(logger:Logger, wait:int, priorcalls:int):
	logger.cap("error.")
	logger.log(f"Database is busy - trying again in {wait}s... ", level=Logger.ERROR, endline=False)
	
	sleep(wait)
	return True
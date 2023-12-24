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
	def __init__(self, dbpath:str, flags:int=None):
		try: 
			if flags: self._connection = apsw.Connection(dbpath, flags=flags)	
			else: self._connection = apsw.Connection(dbpath)	
		
		except apsw.CantOpenError as e: # failed to initialize database
			raise e


	# initialize tables and defaults
	def initialize(self):
		# initialize polling data packet table
		self._connection.execute("""CREATE TABLE IF NOT EXISTS packets (
				id INTEGER PRIMARY KEY,
				timestamp TEXT NOT NULL,
				type TEXT NOT NULL,
				data TEXT NOT NULL,
				UNIQUE(timestamp, type) ON CONFLICT IGNORE
		);""")

		# initialize metadata table
		self._connection.execute("""CREATE TABLE IF NOT EXISTS meta (
				id INTEGER PRIMARY KEY,
				type TEXT NOT NULL UNIQUE,
				value TEXT
		);""")

		# insert default metadata if necessary
		self._connection.execute("INSERT OR IGNORE INTO meta (type, value) VALUES (?,?)", ("lastsync", "0"))


	# error-handling wrapper for execute
	def execute(self, query:str, bindings:tuple[str]=()) -> apsw.Cursor:
		try:
			return self._connection.execute(query, bindings)
		
		# failed to write to database
		except apsw.ReadOnlyError as e0:			
			try: # check if can open db, if yes assume permissions error
				test = apsw.Connection(self._connection.filename, flags=apsw.SQLITE_OPEN_READWRITE)
				raise e0
				
			except apsw.CantOpenError as e1: # otherwise, assume database deleted
				raise e1


# sqlite db busy handler
def busy_handler(logger:Logger, wait:int, priorcalls:int):
	logger.cap("error.")
	logger.log(f"Database is busy - trying again in {wait}s... ", level=Logger.ERROR, endline=False)
	sleep(wait)
	return True
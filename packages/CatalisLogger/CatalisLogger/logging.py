import os
from time import strftime, gmtime


# catalis logger
class Logger:
	# log entry levels
	FATAL, ERROR, WARN, INFO, DEBUG, TRACE, DEFAULT = range(7)
	levels = ["[fatal] ", "[error] ", "[warn] ", "[info] ", "[debug] ", "[trace] ", ""]


	# constructor
	def __init__(self, logfile:str):
		self.logfile = open(logfile, "a+")


	# get open logfile path
	def __str__(self):
		return self.logfile.name


	# check if the last line in the log is terminated
	def previous_line_terminated(self) -> bool:
		# get last char (if possible) to check if previous entry terminated
		try: 
			self.logfile.seek(self.logfile.tell() - 1, os.SEEK_SET)
			return self.logfile.read(1) in ["\n", ""]
		
		except: # beginning of file 
			return True


	# logging function
	def log(self, string:str, level:int=3, force_newline=False, endline:bool=True) -> None:
		is_newline = self.previous_line_terminated()
		
		# prepend timestamp and level if last char newline (ie. this is a new entry)
		if force_newline or is_newline: out = f"""{strftime("%T", gmtime())} | {self.levels[level]}{string}"""
		else: out = f"""{string}"""
		
		# append newline if log entry is completed, prepend if specified
		if force_newline and not is_newline: out = "\n" + out
		print(out, end="\n" if endline else "", file=self.logfile)


	# plain print to logfile
	def print(self, string:str):
		newline = "\n" * (not self.previous_line_terminated())
		print(f"""{newline}{string}""", file=self.logfile)


	# close logfile
	def close(self) -> None:
		self.logfile.close()
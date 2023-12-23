import os
from time import strftime, gmtime
from io import TextIOWrapper


# catalis logger
class Logger:
	# log entry levels
	FATAL, ERROR, WARN, INFO, DEBUG, TRACE, DEFAULT = range(7)
	levels = ["[fatal] ", "[error] ", "[warn] ", "[info] ", "[debug] ", "[trace] ", ""]


	# constructor
	def __init__(self, logfile:str):
		self._logfile = logfile


	# get open logfile path
	def __str__(self):
		return self._logfile


	# check if the last line in the log is terminated
	def previous_line_terminated(self, file:TextIOWrapper) -> bool:
		# get last char (if possible) to check if previous entry terminated
		try: 
			file.seek(file.tell() - 1, os.SEEK_SET)
			return file.read(1) in ["\n", ""]
		
		except: # beginning of file 
			return True


	# logging function
	def log(self, string:str, level:int=3, force_newline=False, endline:bool=True) -> None:
		with open(self._logfile, "a+") as f:
			is_newline = self.previous_line_terminated(f)
			
			# prepend timestamp and level if last char newline (ie. this is a new entry)
			if force_newline or is_newline: out = f"""{strftime("%T", gmtime())} | {self.levels[level]}{string}"""
			else: out = f"""{string}"""
			
			# append newline if log entry is completed, prepend if specified
			if force_newline and not is_newline: out = "\n" + out
			print(out, end="\n" if endline else "", file=f)


	# plain print to logfile
	def print(self, string:str):
		with open(self._logfile, "a+") as f:
			newline = "\n" * (not self.previous_line_terminated(f))
			print(f"""{newline}{string}""", file=f)

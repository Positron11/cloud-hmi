from setuptools import setup, find_packages

setup(
	name="Catalis Logger",
	version="0.1.1",
	description="Logfile creation and management utility for Catalis Systemd daemon services.",
	author="Aarush Kumbhakern",
	license="MIT",
	packages=find_packages(),
	requires=["os", "time"],

	classifiers=[
		"Development Status :: 3 - Alpha",
		"Environment :: Console",
		"Operating System :: POSIX :: Linux",
		"Topic :: System :: Logging"
	]
)
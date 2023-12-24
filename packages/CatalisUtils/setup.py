from setuptools import setup, find_packages

setup(
	name="CatalisUtils",
	version="0.1.3",
	description="Logfile creation and management utility for Catalis CloudHMI daemon services.",
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
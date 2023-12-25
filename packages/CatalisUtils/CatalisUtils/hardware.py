import os
import subprocess as sh


# led object class
class Led():
	GPIO_OFFSET = 454

	# constructor
	def __init__(self, pin:int) -> None:
		self.gpio = pin + self.GPIO_OFFSET

		if not os.path.exists(f"/sys/class/gpio/gpio{self.gpio}"):
			sh.run(f"echo {self.gpio} > /sys/class/gpio/export", shell=True)
			sh.run(f"echo out > /sys/class/gpio/gpio{self.gpio}/direction", shell=True)

	# turn LED on
	def on(self) -> None:
		sh.run(f"echo '1' > /sys/class/gpio/gpio{self.gpio}/value", shell=True)
	
	# turn LED on
	def off(self) -> None:
		sh.run(f"echo '0' > /sys/class/gpio/gpio{self.gpio}/value", shell=True)
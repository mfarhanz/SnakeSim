import tkinter as tk
from typing import Tuple
# from snakesim.src.util.common import Common
from ..util.common import Common

class CustomButton(tk.Button):
	"""
	Button widget supporting pulsing animation.
	"""
	def __init__(self, master=None, pulsebegin="#36454F", pulseend="#00FFFF", pulsebackground=False, **kwargs):
		super().__init__(master, **kwargs)
		__doc__ = tk.Button.__doc__ + "\nThis subclass adds additional functionality."
		self._pulse = False
		self.pulse_background = pulsebackground
		self.initial_color = None
		self.color_start = pulsebegin   # default: charcoal
		self.color_end = pulseend  # default: cyan
		self.pulse_speed = 0.01  # Speed of pulsing
		self.pulse_delay = 5  # Delay between interpolation
		self._progress = 1  # Progress for pulsing (0 to 1)
		self.after_id = None  # Store the after ID for cancellation
	
	@property
	def pulse(self):
		return self._pulse
	
	@pulse.setter
	def pulse(self, value: Tuple[bool, bool]):
		self._pulse = value
		if self._pulse:
			self.initial_color = self.cget("background" if self.pulse_background else "foreground")
			self.pulse_animation()
		else:
			if self.after_id:
				self.after_cancel(self.after_id)
				self.after_id = None
			self.update_color(self.initial_color)
	
	def update_color(self, color):
		if self.pulse_background:
			self.config(bg=color)
		else:
			self.config(fg=color)
	
	def pulse_animation(self):
		if self._pulse:
			# Update the progress
			self._progress += self.pulse_speed
			if self._progress >= 1:  # Reverse direction if it reaches 1
				self._progress = 1
				self.pulse_speed = -self.pulse_speed
			elif self._progress <= 0:  # Reverse direction if it reaches 0
				self._progress = 0
				self.pulse_speed = -self.pulse_speed
			new_color = Common.interpolate_color(self.winfo_rgb(self.color_start),
			                                     self.winfo_rgb(self.color_end), self._progress)
			self.update_color(new_color)
			self.after_id = self.after(self.pulse_delay, self.pulse_animation)

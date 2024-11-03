from threading import Thread
from functools import wraps
from random import choice
# from snakesim.src.util.common import AppException
from src.util.common import AppException

class SimWrappers:
	@staticmethod
	def show_loading(func):
		"""
		Decorator to show a loading message while executing the given method in a different thread, and running a
		callback if provided.
		:param func:
		:return:
		"""
		dot_ctr = 0
		
		@wraps(func)
		def wrapper(*args, **kwargs):
			app_instance = args[0]
			
			def check_if_thread_complete():
				if thread.is_alive():
					nonlocal dot_ctr
					dot_ctr = (dot_ctr + 1) % 4
					app_instance.show_message(f"Loading{'.' * dot_ctr}")
					app_instance.root.after(50, check_if_thread_complete)
				else:
					if 'callback' in kwargs:
						if kwargs['callback']:
							if 'callback_args' in kwargs:
								if kwargs['callback_args']:
									kwargs['callback'](*kwargs['callback_args'])
							else:
								kwargs['callback']()
			thread = Thread(target=func, args=args, kwargs=kwargs)
			thread.start()
			check_if_thread_complete()
			return
		return wrapper
	
	@staticmethod
	def call_safe(func):
		"""
		Decorator that safely calls a function with its parameters and catches exceptions.
		"""
		@wraps(func)
		def wrapper(*args, **kwargs):
			app_instance = args[0]
			try:
				return func(*args, **kwargs)
			except (IndexError, RecursionError, ZeroDivisionError, ValueError, UnboundLocalError, TypeError):
				# Known errors, just print message for now
				app_instance.show_message(f"FATAL ERROR: SnakeSim ran into a problem :(")
		return wrapper

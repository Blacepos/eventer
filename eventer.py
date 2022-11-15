from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

Subscriber = Callable[..., None]
Condition = Callable[..., bool]
Event = Callable[..., Any]

# {fn id -> (before, after, conditions)}
_events: Dict[int, Tuple[List[Subscriber], List[Subscriber], List[Condition]]] = {}

class EventNotRegistered(Exception):
	pass

def event(f: Event) -> Event:
	'''
	# event
	Transforms a function into an event. Does nothing by itself, but enables
	it to be used as a target for `run_before`, `run_after`, and
	`condition_for`.

	## Limitations:
	In the case of class methods, it is not possible to subscribe to a single
	instance's event. To run only on a specific instance, you would have to
	check that the first argument to the subscriber (`self`) is the same
	instance as the instance in question using the `is` keyword.

	## Example
	```python
	# regular functions

	@event
	def add(x, y):
	    return x, y
	
	@run_before(add)
	def print_args(*args, **kwargs):
	    print(args, kwargs)


	# class methods

	class Ball:

	    @event
	    def roll(self):
	        pass
	
	@run_after(Ball.roll)
	def on_roll(self):
	    print(type(self))
	
	
	b = Ball()
	b.roll()
	```
	'''
	@wraps(f)
	def calls_subs(*args, **kwargs):
		before, after, conditions = _events[id(calls_subs)]

		for sub in conditions:
			if not sub(*args, **kwargs):
				return

		for sub in before:
			sub(*args, **kwargs)
		
		r = f(*args, **kwargs)

		for sub in after:
			sub(*args, **kwargs)
		
		return r

	# calls_subs is the function everyone else sees, so it is the one added to
	# _events
	_events[id(calls_subs)] = ([], [], [])

	return calls_subs


def run_before(ev: Event, fn: Optional[Subscriber]=None):
	'''
	# run_before
	Registers a function to run before an event and receive the same arguments.
	This function can be used as a decorator if you own the event or as a plain
	function call if you don't. The syntax can be seen in the example.

	## Example
	```python
	@event
	def add(x, y):
	    return x + y

	@run_before(add)
	def print_args(*args, **kwargs):
	    print(args, kwargs)

	# This syntax can be used to add a function after the definition
	run_before(add, print_args)
	```
	'''
	def decorator(f: Subscriber) -> Subscriber:
		if id(ev) not in _events:
			raise EventNotRegistered(f"Function `{ev.__name__}` is not registered as an event. This can be resolved by adding the `@event` decorator to the function.")
		
		_events[id(ev)][0].append(f)

		return f
	
	# this function is not being used as a decorator if fn is a function
	if fn is not None:
		decorator(fn)

	return decorator


def run_after(ev: Event, fn: Optional[Subscriber]=None):
	'''
	# run_after
	Registers a function to run after an event and receive the same arguments.
	This function can be used as a decorator if you own the event or as a plain
	function call if you don't. The syntax can be seen in the example.

	## Example
	```python
	@event
	def add(x, y):
	    return x + y

	@run_after(add)
	def print_args(*args, **kwargs):
	    print(args, kwargs)

	# This syntax can be used to add a function after the definition
	run_after(add, print_args)
	```
	'''
	def decorator(f: Subscriber) -> Subscriber:
		if id(ev) not in _events:
			raise EventNotRegistered(f"Function `{ev.__name__}` is not registered as an event. This can be resolved by adding the `@event` decorator to the function.")
		
		_events[id(ev)][1].append(f)

		return f
	
	# this function is not being used as a decorator if fn is a function
	if fn is not None:
		decorator(fn)

	return decorator


def condition_for(ev: Event, fn: Optional[Condition]=None):
	'''
	# condition_for
	Allows a function to block the execution of an event based on event
	arguments. This function can be used as a decorator if you own the event or
	as a plain function call if you don't. The syntax can be seen in the
	example.

	## Warning
	Use this with caution, as the event in question will not be able to return
	a value. It is suggested to only use this for events that don't return
	anything.

	## Example
	```python
	@event
	def print_addition(x, y):
	    print(x + y)

	@condition_for(print_addition)
	def avoid_2s(x, y):
	    return x != 2 and y != 2

	# This syntax can be used to add a function after the definition
	condition_for(print_addition, avoid_2s)
	```
	'''
	def decorator(f: Condition) -> Condition:
		if id(ev) not in _events:
			raise EventNotRegistered(f"Function `{ev.__name__}` is not registered as an event. This can be resolved by adding the `@event` decorator to the function.")
		
		_events[id(ev)][2].append(f)

		return f
	
	# this function is not being used as a decorator if fn is a function
	if fn is not None:
		decorator(fn)

	return decorator


def voidargs(f: Callable[..., Any]) -> Callable[[], None]:
	'''
	# voidargs
	Transforms a function that takes no arguments into a function that accepts
	any arguments and voids them. May be useful when registering a function as
	a subscriber that doesn't take any arguments. This also voids return values.

	## Example
	```python
	
	@event
	def add(x, y):
	    return x + y

	@run_after(add)
	@voidargs
	def say_hi():  # would have needed (*args, **kwargs) without @voidargs
	    print("hi")
	```
	'''
	@wraps(f)
	def voided(*args, **kwargs):
		f()

	return voided


def _print_args(*args, **kwargs):
    print("Args:",args," Keyword Args:",kwargs)

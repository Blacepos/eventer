from operator import itemgetter
import unittest
from eventer import *
from eventer import _events

sorted0 = lambda it: sorted(it, key=itemgetter(0))

def events_sorted():
	return sorted0(_events.items())

class TestEventer(unittest.TestCase):
	def test_add_event(self):

		@event
		def foo():
			pass

		def bar():
			pass

		self.assertEqual([(id(foo), ([],[],[]))], events_sorted())

		@run_before(foo)
		def sub1():
			pass
		@run_after(foo)
		def sub2():
			pass
		@condition_for(foo)
		def cond1():
			return True

		with self.assertRaises(EventNotRegistered):
			@run_before(bar)
			def subx():
				pass
		with self.assertRaises(EventNotRegistered):
			@run_after(bar)
			def subx():
				pass
		with self.assertRaises(EventNotRegistered):
			@condition_for(bar)
			def condx():
				return True
		
		self.assertEqual([(id(foo), ([sub1],[sub2],[cond1]))], events_sorted())

		run_before(foo, sub2)
		run_after(foo, cond1)  # type: ignore
		condition_for(foo, sub1)  # type: ignore

		self.assertEqual([(id(foo), ([sub1, sub2],[sub2, cond1],[cond1, sub1]))], events_sorted())

		@event
		def baz():
			pass
		
		expected = [(id(foo), ([sub1, sub2],[sub2, cond1],[cond1, sub1])), (id(baz), ([], [], []))]
		self.assertEqual(sorted0(expected), events_sorted())

		run_before(baz, sub2)
		run_after(baz, cond1)  # type: ignore
		condition_for(baz, sub1)  # type: ignore

		expected = [(id(foo), ([sub1, sub2],[sub2, cond1],[cond1, sub1])), (id(baz), ([sub2], [cond1], [sub1]))]
		self.assertEqual(sorted0(expected), events_sorted())

		# check return value
		@event
		def return5():
			return 5

		self.assertEqual(return5(), 5)
		
	
	def test_run_before_and_after(self):
		global _events
		# check that subscribers are passed arguments

		@event
		def foo(x, y=5):
			return x * 2 + y
		
		@run_before(foo)
		@run_after(foo)
		def check_args1(*args, **kwargs):
			self.assertEqual((1,), args)
			self.assertEqual({}, kwargs)
		
		foo(1)

		@event
		def foo2(x, y=5):
			return x * 2 + y
		
		@run_before(foo2)
		@run_after(foo2)
		def check_args2(*args, **kwargs):
			self.assertEqual((1,15), args)
			self.assertEqual({}, kwargs)
		
		foo2(1,15)

		@event
		def foo3(x, y=5):
			return x * 2 + y

		@run_before(foo3)
		@run_after(foo3)
		def check_args3(*args, **kwargs):
			self.assertEqual((1,), args)
			self.assertEqual({"y": 15}, kwargs)
		
		foo3(1,y=15)

		# more complex test checking the order of execution

		x = 5
		def increment():
			nonlocal x
			x += 1

		@event
		def zero_if_6():
			nonlocal x
			if x == 6:
				x = 0

		run_after(zero_if_6, increment)

		self.assertEqual(5, x)
		zero_if_6()
		self.assertEqual(6, x)

		run_before(zero_if_6, increment)

		x = 5
		self.assertEqual(5, x)
		zero_if_6()
		self.assertEqual(1, x)

	def test_condition(self):

		# conditional execution checks
		
		x = 50

		@event
		def set_x_to_0():
			nonlocal x
			x = 0
		
		set_x_to_0()
		self.assertEqual(0, x)

		x = 50

		@condition_for(set_x_to_0)
		def always_false():
			return False

		set_x_to_0()
		self.assertEqual(50, x)

		@event
		def set_x_to_arg(arg):
			nonlocal x
			x = arg
		
		set_x_to_arg(10)
		self.assertEqual(10, x)

		x = 50

		@condition_for(set_x_to_arg)
		def is_even(arg):
			return arg % 2 == 0
		
		for n in range(10):
			prev = x
			set_x_to_arg(n)
			if is_even(n):
				self.assertEqual(n, x)
			else:
				self.assertEqual(prev, x)
		

		# check return value

		@event
		def return5():
			return 5

		self.assertEqual(return5(), 5)

		condition_for(return5, always_false)

		self.assertEqual(return5(), None)

		# check that other subscribers are not run
		
		x = 0

		@event
		def foo():
			pass
		
		@run_before(foo)
		@run_after(foo)
		def sub1():
			nonlocal x
			x += 1

		foo()
		self.assertEqual(x, 2)

		condition_for(foo, always_false)
		
		foo()
		self.assertEqual(x, 2)


if __name__ == "__main__":
	unittest.main()

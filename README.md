# Eventer

An easy-to-use event registrar

## Example

```python
from eventer import *
# Register regular functions

@event
def add(x, y):
    return x, y

@run_before(add)
def print_args(*args, **kwargs):
    print(args, kwargs)

print(add(2,3))  # calls print_args with (2,3) then prints "5"


# Register class methods

class Ball:

    @event
    def roll(self):
        pass

@run_after(Ball.roll)
def on_roll(self):
    print(type(self))


b = Ball()
b.roll()
# ^ causes `on_roll` to be invoked with `self` as `b`


# Add execution conditions
@event
def say_hello(name):
    print(f"hello {name}!")

@condition_for(say_hello)
def ignore_josh(name):
    return name != "josh"

say_hello("timothy")  # "hello timothy!" is printed
say_hello("josh")  # nothing is printed


# Subscribe with functions you don't own
@event
def cool_event():
	pass

# literally couldn't be me
def no_decorators():
    print("how boring")

run_before(cool_event, no_decorators)

cool_event()  # "how boring" is printed
```
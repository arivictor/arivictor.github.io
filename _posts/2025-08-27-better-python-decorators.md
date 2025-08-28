---
layout: post
title:  "Better Python Decorators - Basic and Advanced Patterns"
date: 2025-08-28 12:00:00 +1000
description: "Use Python decorators to write cleaner, more modular code. Learn to create, chain, and optimize decorators for real-world use cases."
tags:
    - python
    - decorators
    - programming
    - tutorial
---

Decorators are one of Python's most powerful and elegant features. They allow you to modify or enhance functions and classes without changing their core implementation. Think of them as wrappers that add functionality—like adding superpowers to your code.

## Understanding Decorators

At their core, decorators are functions that take another function as an argument and return a modified version of that function.

```python
# Basic decorator concept
def my_decorator(func):
    def wrapper():
        print("Something before the function")
        func()
        print("Something after the function")
    return wrapper

# Using the decorator
@my_decorator
def say_hello():
    print("Hello!")

# This is equivalent to:
# say_hello = my_decorator(say_hello)

say_hello()
# Output:
# Something before the function
# Hello!
# Something after the function
```

## Simple Decorators

### Timing Decorator

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done!"

result = slow_function()
# Output: slow_function took 1.0041 seconds
```

### Logging Decorator

```python
import logging
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logging.error(f"{func.__name__} raised: {e}")
            raise
    return wrapper

@log_calls
def divide(a, b):
    return a / b

# Configure logging
logging.basicConfig(level=logging.INFO)
result = divide(10, 2)  # Logs the call and result
```

## Decorators with Arguments

Sometimes you need to configure your decorators. This requires an additional layer of functions:

```python
def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_attempts} attempts failed.")
            
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def unreliable_api_call():
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("API is down")
    return "Success!"

# Usage
try:
    result = unreliable_api_call()
    print(result)
except ConnectionError as e:
    print(f"Final failure: {e}")
```

## Class-Based Decorators

You can also create decorators using classes:

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} has been called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    return f"Hello, {name}!"

greet("Alice")  # greet has been called 1 times
greet("Bob")    # greet has been called 2 times
greet("Charlie") # greet has been called 3 times
```

## Advanced Decorator Patterns

### Caching/Memoization

```python
from functools import wraps
import time

def memoize(func):
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a key from arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            print(f"Cache hit for {func.__name__}")
            return cache[key]
        
        print(f"Computing {func.__name__}")
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    # Add cache inspection methods
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Usage
print(fibonacci(10))  # Computes once
print(fibonacci(10))  # Uses cache
print(f"Cache size: {len(fibonacci.cache)}")
```

### Rate Limiting

```python
import time
from collections import defaultdict
from functools import wraps

def rate_limit(calls_per_second=1):
    def decorator(func):
        call_times = defaultdict(list)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            func_name = func.__name__
            
            # Clean old calls
            call_times[func_name] = [
                call_time for call_time in call_times[func_name]
                if now - call_time < 1.0
            ]
            
            # Check rate limit
            if len(call_times[func_name]) >= calls_per_second:
                sleep_time = 1.0 - (now - call_times[func_name][0])
                if sleep_time > 0:
                    print(f"Rate limit hit. Sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    now = time.time()
            
            call_times[func_name].append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
def api_call(endpoint):
    print(f"Calling API endpoint: {endpoint}")
    return f"Data from {endpoint}"

# Test rate limiting
for i in range(5):
    api_call(f"/endpoint{i}")
```

### Validation Decorator

```python
from functools import wraps
import inspect

def validate_types(**type_checks):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate types
            for param_name, expected_type in type_checks.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"Parameter '{param_name}' must be of type "
                            f"{expected_type.__name__}, got {type(value).__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int, height=float)
def create_person(name, age, height=0.0):
    return f"Person: {name}, Age: {age}, Height: {height}m"

# Valid calls
person1 = create_person("Alice", 25, 1.65)
person2 = create_person("Bob", 30)

# Invalid call - will raise TypeError
try:
    person3 = create_person("Charlie", "25")  # age should be int
except TypeError as e:
    print(f"Validation error: {e}")
```

## Decorator Chaining

You can apply multiple decorators to a single function:

```python
@timer
@log_calls
@retry(max_attempts=2)
def complex_operation(x, y):
    if x < 0:
        raise ValueError("x must be positive")
    return x ** y

# This is equivalent to:
# complex_operation = timer(log_calls(retry(max_attempts=2)(complex_operation)))

result = complex_operation(2, 3)
```

## Property Decorators

Python's built-in property decorator is a great example of decorators in action:

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self):
        return self._celsius + 273.15

# Usage
temp = Temperature(25)
print(f"Celsius: {temp.celsius}")     # 25
print(f"Fahrenheit: {temp.fahrenheit}") # 77.0
print(f"Kelvin: {temp.kelvin}")       # 298.15

temp.fahrenheit = 100
print(f"Celsius: {temp.celsius}")     # 37.777...
```

## Decorators for Classes

You can also decorate entire classes:

```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, host="localhost"):
        self.host = host
        print(f"Creating connection to {host}")
    
    def query(self, sql):
        return f"Executing: {sql} on {self.host}"

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection("remote-host")  # Same instance as db1
print(db1 is db2)  # True
```

### Auto-property Decorator

```python
def auto_properties(cls):
    """Automatically create properties for private attributes."""
    for name in dir(cls):
        if name.startswith('_') and not name.startswith('__'):
            attr_name = name[1:]  # Remove leading underscore
            
            def make_property(attr):
                def getter(self):
                    return getattr(self, f'_{attr}')
                
                def setter(self, value):
                    setattr(self, f'_{attr}', value)
                
                return property(getter, setter)
            
            setattr(cls, attr_name, make_property(attr_name))
    
    return cls

@auto_properties
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age

# Usage
person = Person("Alice", 30)
print(person.name)  # Alice (via auto-generated property)
person.age = 31     # Uses auto-generated setter
print(person.age)   # 31
```

## Real-World Examples

### Authentication Decorator

```python
from functools import wraps

def requires_auth(permission_level="user"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # In a real app, you'd check session, JWT token, etc.
            current_user = get_current_user()  # Placeholder function
            
            if not current_user:
                raise PermissionError("Authentication required")
            
            if not has_permission(current_user, permission_level):
                raise PermissionError(f"Requires {permission_level} level access")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@requires_auth("admin")
def delete_user(user_id):
    return f"User {user_id} deleted"

@requires_auth("user")
def view_profile():
    return "Profile data"
```

### API Endpoint Decorator

```python
from functools import wraps
import json

def api_endpoint(methods=None, content_type="application/json"):
    if methods is None:
        methods = ["GET"]
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Validate HTTP method
            if request.method not in methods:
                return {"error": "Method not allowed"}, 405
            
            # Parse JSON for POST/PUT requests
            if request.method in ["POST", "PUT"] and content_type == "application/json":
                try:
                    request.json = json.loads(request.body)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON"}, 400
            
            try:
                result = func(request, *args, **kwargs)
                return result if isinstance(result, tuple) else (result, 200)
            except Exception as e:
                return {"error": str(e)}, 500
        
        return wrapper
    return decorator

@api_endpoint(methods=["GET", "POST"])
def user_endpoint(request):
    if request.method == "GET":
        return {"users": ["Alice", "Bob", "Charlie"]}
    elif request.method == "POST":
        return {"message": f"Created user: {request.json['name']}"}
```

### Performance Monitoring

```python
import time
import psutil
from functools import wraps
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self):
        self.stats = defaultdict(list)
    
    def monitor(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            start_time = time.time()
            start_memory = process.memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                raise
            finally:
                end_time = time.time()
                end_memory = process.memory_info().rss
                
                self.stats[func.__name__].append({
                    'duration': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'success': success,
                    'timestamp': start_time
                })
            
            return result
        return wrapper
    
    def get_stats(self, func_name):
        if func_name not in self.stats:
            return None
        
        data = self.stats[func_name]
        return {
            'call_count': len(data),
            'avg_duration': sum(d['duration'] for d in data) / len(data),
            'success_rate': sum(d['success'] for d in data) / len(data),
            'avg_memory_delta': sum(d['memory_delta'] for d in data) / len(data)
        }

# Usage
monitor = PerformanceMonitor()

@monitor.monitor
def expensive_calculation(n):
    return sum(i**2 for i in range(n))

# Run some tests
for i in range(5):
    expensive_calculation(100000)

print(monitor.get_stats('expensive_calculation'))
```

## Best Practices

### 1. Use `functools.wraps`

Always use `@wraps(func)` to preserve the original function's metadata:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # This is important!
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def example_function():
    """This docstring will be preserved."""
    pass

print(example_function.__name__)  # 'example_function' (not 'wrapper')
print(example_function.__doc__)   # 'This docstring will be preserved.'
```

### 2. Handle Arguments Properly

Use `*args` and `**kwargs` to handle any function signature:

```python
def universal_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Pre-processing
        result = func(*args, **kwargs)
        # Post-processing
        return result
    return wrapper
```

### 3. Keep Decorators Simple

```python
# Good: Simple and focused
def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Avoid: Complex decorators with multiple responsibilities
def complex_decorator(func):
    # Too much logic here makes it hard to test and maintain
    pass
```

### 4. Make Decorators Configurable

```python
def configurable_decorator(option1=None, option2=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if option2:
                # Different behavior based on configuration
                pass
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Common Pitfalls

### 1. Decorator vs. Decorator Factory Confusion

```python
# Decorator (no parentheses)
@timer
def function1():
    pass

# Decorator factory (with parentheses)
@retry(max_attempts=3)
def function2():
    pass

# This won't work as expected:
@retry  # Missing parentheses - passes function to retry instead of decorator
def function3():
    pass
```

### 2. Modifying Mutable Default Arguments

```python
# Problematic
def cache_decorator(func, cache={}):  # Shared mutable default!
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args in cache:
            return cache[args]
        result = func(*args, **kwargs)
        cache[args] = result
        return result
    return wrapper

# Better
def cache_decorator(func):
    cache = {}  # Each decorated function gets its own cache
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args in cache:
            return cache[args]
        result = func(*args, **kwargs)
        cache[args] = result
        return result
    return wrapper
```

## Conclusion

Decorators are a powerful tool for writing clean, modular Python code. They allow you to:

- Separate concerns (logging, timing, authentication)
- Add functionality without modifying existing code
- Create reusable components
- Implement cross-cutting concerns elegantly

Key principles:

- Use `@wraps` to preserve function metadata
- Keep decorators simple and focused
- Use `*args` and `**kwargs` for flexibility
- Make decorators configurable when needed
- Test decorators thoroughly

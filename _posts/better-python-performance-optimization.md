---
layout: post
title: "Better Python: Performance Optimization Techniques"
date: 2025-03-19
summary: "Master Python performance optimization from profiling and measurement to advanced techniques. Learn when and how to make your Python code faster."
categories: python programming performance optimization profiling better-python
---

# The Art of Making Python Fast

Performance optimization in Python is about making informed decisions based on measurement, not assumptions. Before optimizing anything, you need to know where the bottlenecks are, why they exist, and whether the optimization will actually matter. This post covers the complete journey from profiling to optimization.

## The First Rule: Measure, Don't Guess

```python
import time
import cProfile
import pstats
from functools import wraps
from typing import Callable, Any

def timer(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__} took {end_time - start_time:.6f} seconds")
        return result
    return wrapper

# Example usage
@timer
def slow_function():
    """Simulate a slow function."""
    total = 0
    for i in range(1000000):
        total += i ** 2
    return total

@timer
def fast_function():
    """Optimized version using mathematical formula."""
    n = 1000000
    # Formula for sum of squares: n(n+1)(2n+1)/6
    return n * (n - 1) * (2 * n - 1) // 6

# Compare performance
slow_result = slow_function()
fast_result = fast_function()
print(f"Results match: {slow_result == fast_result}")
```

## Profiling Tools and Techniques

### Using cProfile

```python
import cProfile
import pstats
import io

def profile_function(func, *args, **kwargs):
    """Profile a function and return detailed statistics."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    # Create string buffer to capture profile output
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats()
    
    print(s.getvalue())
    return result

def complex_calculation():
    """Function with multiple performance bottlenecks."""
    # Expensive string operations
    text = ""
    for i in range(10000):
        text += f"Item {i}, "
    
    # Inefficient list operations
    numbers = []
    for i in range(10000):
        numbers.append(i ** 2)
    
    # Nested loops
    result = 0
    for i in range(100):
        for j in range(100):
            result += i * j
    
    return len(text), len(numbers), result

# Profile the function
profile_function(complex_calculation)
```

### Line-by-Line Profiling with line_profiler

```python
"""
Install: pip install line_profiler

Usage:
1. Add @profile decorator to functions
2. Run: kernprof -l -v script.py
"""

@profile
def string_operations_comparison():
    """Compare different string building methods."""
    
    # Method 1: String concatenation (slow)
    result1 = ""
    for i in range(10000):
        result1 += str(i)
    
    # Method 2: List join (fast)
    items = []
    for i in range(10000):
        items.append(str(i))
    result2 = "".join(items)
    
    # Method 3: List comprehension + join (fastest)
    result3 = "".join(str(i) for i in range(10000))
    
    return len(result1), len(result2), len(result3)
```

### Memory Profiling

```python
from memory_profiler import profile
import tracemalloc

@profile
def memory_intensive_function():
    """Function that uses lots of memory."""
    # Create large lists
    big_list = [i for i in range(1000000)]
    
    # Create dictionary
    big_dict = {i: i**2 for i in range(100000)}
    
    # String operations
    big_string = "x" * 1000000
    
    return len(big_list), len(big_dict), len(big_string)

def trace_memory_usage(func, *args, **kwargs):
    """Trace memory usage of a function."""
    tracemalloc.start()
    
    result = func(*args, **kwargs)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    return result

# Example usage
trace_memory_usage(memory_intensive_function)
```

## Data Structure Optimization

### Choosing the Right Data Structure

```python
import timeit
from collections import deque, defaultdict, Counter
from typing import List, Set, Dict

def benchmark_data_structures():
    """Compare performance of different data structures."""
    
    # List vs Set for membership testing
    large_list = list(range(10000))
    large_set = set(range(10000))
    
    # Test membership
    list_time = timeit.timeit(lambda: 9999 in large_list, number=1000)
    set_time = timeit.timeit(lambda: 9999 in large_set, number=1000)
    
    print(f"List membership: {list_time:.6f}s")
    print(f"Set membership: {set_time:.6f}s")
    print(f"Set is {list_time/set_time:.1f}x faster")
    
    # List vs Deque for front operations
    test_list = []
    test_deque = deque()
    
    # Insert at beginning
    list_insert_time = timeit.timeit(lambda: test_list.insert(0, 1), number=10000)
    deque_insert_time = timeit.timeit(lambda: test_deque.appendleft(1), number=10000)
    
    print(f"\nList insert at front: {list_insert_time:.6f}s")
    print(f"Deque insert at front: {deque_insert_time:.6f}s")
    print(f"Deque is {list_insert_time/deque_insert_time:.1f}x faster")

# Dictionary optimization
class OptimizedLookup:
    def __init__(self):
        self.data = {}
        self.default_dict = defaultdict(int)
        self.counter = Counter()
    
    def regular_dict_increment(self, key):
        """Regular dictionary with manual key checking."""
        if key in self.data:
            self.data[key] += 1
        else:
            self.data[key] = 1
    
    def defaultdict_increment(self, key):
        """Using defaultdict for automatic initialization."""
        self.default_dict[key] += 1
    
    def counter_increment(self, key):
        """Using Counter for counting operations."""
        self.counter[key] += 1

def compare_dict_operations():
    """Compare different dictionary operation patterns."""
    optimizer = OptimizedLookup()
    keys = ['a', 'b', 'c'] * 1000
    
    # Time different approaches
    regular_time = timeit.timeit(
        lambda: [optimizer.regular_dict_increment(k) for k in keys], 
        number=100
    )
    
    defaultdict_time = timeit.timeit(
        lambda: [optimizer.defaultdict_increment(k) for k in keys], 
        number=100
    )
    
    counter_time = timeit.timeit(
        lambda: [optimizer.counter_increment(k) for k in keys], 
        number=100
    )
    
    print(f"Regular dict: {regular_time:.6f}s")
    print(f"DefaultDict: {defaultdict_time:.6f}s")
    print(f"Counter: {counter_time:.6f}s")

benchmark_data_structures()
compare_dict_operations()
```

### Efficient Data Processing

```python
import numpy as np
from typing import List, Iterator

class DataProcessor:
    @staticmethod
    def process_list_traditional(data: List[int]) -> List[int]:
        """Traditional Python list processing."""
        result = []
        for item in data:
            if item % 2 == 0:
                result.append(item ** 2)
        return result
    
    @staticmethod
    def process_list_comprehension(data: List[int]) -> List[int]:
        """List comprehension approach."""
        return [item ** 2 for item in data if item % 2 == 0]
    
    @staticmethod
    def process_list_generator(data: List[int]) -> Iterator[int]:
        """Generator expression for memory efficiency."""
        return (item ** 2 for item in data if item % 2 == 0)
    
    @staticmethod
    def process_numpy(data: List[int]) -> np.ndarray:
        """NumPy vectorized operations."""
        arr = np.array(data)
        even_mask = arr % 2 == 0
        return arr[even_mask] ** 2
    
    @staticmethod
    def process_with_filter_map(data: List[int]) -> List[int]:
        """Using filter and map functions."""
        return list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, data)))

def benchmark_processing_methods():
    """Compare different data processing approaches."""
    data = list(range(100000))
    processor = DataProcessor()
    
    methods = [
        ("Traditional", processor.process_list_traditional),
        ("List Comprehension", processor.process_list_comprehension),
        ("Generator", lambda d: list(processor.process_list_generator(d))),
        ("NumPy", processor.process_numpy),
        ("Filter/Map", processor.process_with_filter_map)
    ]
    
    for name, method in methods:
        time_taken = timeit.timeit(lambda: method(data), number=100)
        print(f"{name}: {time_taken:.6f}s")

benchmark_processing_methods()
```

## Algorithm Optimization

### Caching and Memoization

```python
from functools import lru_cache, wraps
from typing import Dict, Any
import time

# Manual memoization
def memoize(func):
    """Manual memoization decorator."""
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper

# Compare memoization approaches
@memoize
def fibonacci_manual_memo(n):
    """Fibonacci with manual memoization."""
    if n < 2:
        return n
    return fibonacci_manual_memo(n-1) + fibonacci_manual_memo(n-2)

@lru_cache(maxsize=None)
def fibonacci_lru_cache(n):
    """Fibonacci with LRU cache."""
    if n < 2:
        return n
    return fibonacci_lru_cache(n-1) + fibonacci_lru_cache(n-2)

def fibonacci_iterative(n):
    """Iterative fibonacci - no caching needed."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def compare_fibonacci_approaches():
    """Compare different fibonacci implementations."""
    n = 35
    
    # Clear caches
    fibonacci_manual_memo.cache_clear()
    fibonacci_lru_cache.cache_clear()
    
    approaches = [
        ("Manual Memoization", fibonacci_manual_memo),
        ("LRU Cache", fibonacci_lru_cache),
        ("Iterative", fibonacci_iterative)
    ]
    
    for name, func in approaches:
        start_time = time.perf_counter()
        result = func(n)
        end_time = time.perf_counter()
        print(f"{name}: {end_time - start_time:.6f}s, result: {result}")

compare_fibonacci_approaches()
```

### Set Operations and Lookups

```python
def optimize_lookups():
    """Demonstrate efficient lookup patterns."""
    
    # Large dataset for testing
    data = list(range(100000))
    lookup_values = list(range(50000, 60000))
    
    # Method 1: Linear search in list (slow)
    def linear_search():
        return [x for x in lookup_values if x in data]
    
    # Method 2: Set intersection (fast)
    def set_intersection():
        data_set = set(data)
        lookup_set = set(lookup_values)
        return list(data_set.intersection(lookup_set))
    
    # Method 3: Set comprehension (fast)
    def set_comprehension():
        data_set = set(data)
        return [x for x in lookup_values if x in data_set]
    
    methods = [
        ("Linear Search", linear_search),
        ("Set Intersection", set_intersection),
        ("Set Comprehension", set_comprehension)
    ]
    
    for name, method in methods:
        time_taken = timeit.timeit(method, number=10)
        print(f"{name}: {time_taken:.6f}s")

optimize_lookups()
```

## String and I/O Optimization

### String Building Optimization

```python
import io

class StringOptimizer:
    @staticmethod
    def concat_with_plus(items):
        """String concatenation with + operator (slow)."""
        result = ""
        for item in items:
            result += str(item)
        return result
    
    @staticmethod
    def concat_with_join(items):
        """String concatenation with join (fast)."""
        return "".join(str(item) for item in items)
    
    @staticmethod
    def concat_with_list(items):
        """Build list then join (fast, memory-efficient)."""
        parts = []
        for item in items:
            parts.append(str(item))
        return "".join(parts)
    
    @staticmethod
    def concat_with_stringio(items):
        """Using StringIO for building strings."""
        buffer = io.StringIO()
        for item in items:
            buffer.write(str(item))
        return buffer.getvalue()
    
    @staticmethod
    def format_with_fstring(items):
        """Using f-string formatting."""
        return "".join(f"{item}" for item in items)

def benchmark_string_operations():
    """Compare string building methods."""
    items = list(range(10000))
    optimizer = StringOptimizer()
    
    methods = [
        ("Plus Operator", optimizer.concat_with_plus),
        ("Join Method", optimizer.concat_with_join),
        ("List + Join", optimizer.concat_with_list),
        ("StringIO", optimizer.concat_with_stringio),
        ("F-string", optimizer.format_with_fstring)
    ]
    
    for name, method in methods:
        time_taken = timeit.timeit(lambda: method(items), number=100)
        print(f"{name}: {time_taken:.6f}s")

benchmark_string_operations()
```

### File I/O Optimization

```python
import os
import tempfile

class FileOptimizer:
    @staticmethod
    def read_line_by_line(filename):
        """Read file line by line (memory efficient)."""
        with open(filename, 'r') as f:
            return [line.strip() for line in f]
    
    @staticmethod
    def read_all_at_once(filename):
        """Read entire file at once (fast but memory intensive)."""
        with open(filename, 'r') as f:
            return f.read().splitlines()
    
    @staticmethod
    def read_with_buffer(filename, buffer_size=8192):
        """Read with custom buffer size."""
        with open(filename, 'r', buffering=buffer_size) as f:
            return f.read().splitlines()
    
    @staticmethod
    def write_line_by_line(filename, lines):
        """Write lines one by one."""
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line + '\n')
    
    @staticmethod
    def write_with_join(filename, lines):
        """Write all lines at once."""
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
    
    @staticmethod
    def write_with_writelines(filename, lines):
        """Write using writelines."""
        with open(filename, 'w') as f:
            f.writelines(line + '\n' for line in lines)

def benchmark_file_operations():
    """Compare file I/O methods."""
    # Create test data
    test_lines = [f"Line {i} with some content" for i in range(10000)]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.txt")
        
        # First write the file
        FileOptimizer.write_with_join(test_file, test_lines)
        
        optimizer = FileOptimizer()
        
        # Test reading methods
        read_methods = [
            ("Line by Line", optimizer.read_line_by_line),
            ("All at Once", optimizer.read_all_at_once),
            ("Custom Buffer", lambda f: optimizer.read_with_buffer(f, 16384))
        ]
        
        print("Reading Methods:")
        for name, method in read_methods:
            time_taken = timeit.timeit(lambda: method(test_file), number=100)
            print(f"  {name}: {time_taken:.6f}s")
        
        # Test writing methods
        write_methods = [
            ("Line by Line", optimizer.write_line_by_line),
            ("Join Method", optimizer.write_with_join),
            ("Write Lines", optimizer.write_with_writelines)
        ]
        
        print("\nWriting Methods:")
        for name, method in write_methods:
            write_file = os.path.join(temp_dir, f"write_test_{name.replace(' ', '_').lower()}.txt")
            time_taken = timeit.timeit(lambda: method(write_file, test_lines), number=100)
            print(f"  {name}: {time_taken:.6f}s")

benchmark_file_operations()
```

## Parallel Processing and Concurrency

### CPU-Bound Tasks with Multiprocessing

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import math

def cpu_intensive_task(n):
    """CPU-intensive task for testing parallelization."""
    result = 0
    for i in range(n):
        result += math.sqrt(i) * math.sin(i)
    return result

def compare_parallel_processing():
    """Compare different parallel processing approaches."""
    tasks = [100000] * 8  # 8 tasks of equal size
    
    # Sequential processing
    start_time = time.perf_counter()
    sequential_results = [cpu_intensive_task(n) for n in tasks]
    sequential_time = time.perf_counter() - start_time
    
    # Multiprocessing with ProcessPoolExecutor
    start_time = time.perf_counter()
    with ProcessPoolExecutor() as executor:
        parallel_results = list(executor.map(cpu_intensive_task, tasks))
    parallel_time = time.perf_counter() - start_time
    
    # Multiprocessing with Pool
    start_time = time.perf_counter()
    with mp.Pool() as pool:
        pool_results = pool.map(cpu_intensive_task, tasks)
    pool_time = time.perf_counter() - start_time
    
    print(f"Sequential: {sequential_time:.2f}s")
    print(f"ProcessPoolExecutor: {parallel_time:.2f}s")
    print(f"Multiprocessing Pool: {pool_time:.2f}s")
    print(f"Speedup (ProcessPool): {sequential_time/parallel_time:.2f}x")
    print(f"Speedup (Pool): {sequential_time/pool_time:.2f}x")
    
    # Verify results are the same
    assert sequential_results == parallel_results == pool_results

compare_parallel_processing()
```

### I/O-Bound Tasks with Threading

```python
import asyncio
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

def simulate_io_task(task_id, duration=1):
    """Simulate I/O-bound task."""
    time.sleep(duration)
    return f"Task {task_id} completed"

def compare_io_concurrency():
    """Compare different approaches for I/O-bound tasks."""
    tasks = list(range(10))
    duration = 0.5
    
    # Sequential execution
    start_time = time.perf_counter()
    sequential_results = [simulate_io_task(i, duration) for i in tasks]
    sequential_time = time.perf_counter() - start_time
    
    # Threading with ThreadPoolExecutor
    start_time = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        thread_results = list(executor.map(lambda i: simulate_io_task(i, duration), tasks))
    thread_time = time.perf_counter() - start_time
    
    print(f"Sequential I/O: {sequential_time:.2f}s")
    print(f"Threading: {thread_time:.2f}s")
    print(f"Threading speedup: {sequential_time/thread_time:.2f}x")

# Async I/O comparison
async def async_io_task(session, task_id):
    """Async I/O task using aiohttp."""
    url = f"http://httpbin.org/delay/0.5"
    async with session.get(url) as response:
        return f"Async task {task_id} completed with status {response.status}"

async def compare_async_io():
    """Compare async I/O with synchronous I/O."""
    task_count = 10
    
    # Synchronous requests
    start_time = time.perf_counter()
    sync_results = []
    for i in range(task_count):
        response = requests.get("http://httpbin.org/delay/0.5")
        sync_results.append(f"Sync task {i} completed with status {response.status_code}")
    sync_time = time.perf_counter() - start_time
    
    # Asynchronous requests
    start_time = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        async_tasks = [async_io_task(session, i) for i in range(task_count)]
        async_results = await asyncio.gather(*async_tasks)
    async_time = time.perf_counter() - start_time
    
    print(f"Synchronous requests: {sync_time:.2f}s")
    print(f"Asynchronous requests: {async_time:.2f}s")
    print(f"Async speedup: {sync_time/async_time:.2f}x")

compare_io_concurrency()
# asyncio.run(compare_async_io())  # Uncomment to test async I/O
```

## NumPy and Vectorization

```python
import numpy as np

class NumpyOptimizer:
    @staticmethod
    def python_loops(data):
        """Pure Python implementation with loops."""
        result = []
        for i in range(len(data)):
            result.append(data[i] ** 2 + 2 * data[i] + 1)
        return result
    
    @staticmethod
    def list_comprehension(data):
        """Python list comprehension."""
        return [x**2 + 2*x + 1 for x in data]
    
    @staticmethod
    def numpy_vectorized(data):
        """NumPy vectorized operations."""
        arr = np.array(data)
        return arr**2 + 2*arr + 1
    
    @staticmethod
    def numpy_polynomial(data):
        """NumPy polynomial evaluation."""
        arr = np.array(data)
        return np.polyval([1, 2, 1], arr)  # x^2 + 2x + 1

def benchmark_vectorization():
    """Compare Python vs NumPy for mathematical operations."""
    data = list(range(100000))
    optimizer = NumpyOptimizer()
    
    methods = [
        ("Python Loops", optimizer.python_loops),
        ("List Comprehension", optimizer.list_comprehension),
        ("NumPy Vectorized", optimizer.numpy_vectorized),
        ("NumPy Polynomial", optimizer.numpy_polynomial)
    ]
    
    print("Mathematical Operations Benchmark:")
    for name, method in methods:
        time_taken = timeit.timeit(lambda: method(data), number=100)
        print(f"  {name}: {time_taken:.6f}s")

# Advanced NumPy operations
def numpy_advanced_optimizations():
    """Demonstrate advanced NumPy optimization techniques."""
    
    # Broadcasting vs loops
    def matrix_operations_loops(a, b):
        """Matrix operations using Python loops."""
        result = []
        for i in range(len(a)):
            row = []
            for j in range(len(b[0])):
                row.append(a[i] + b[0][j])
            result.append(row)
        return result
    
    def matrix_operations_broadcasting(a, b):
        """Matrix operations using NumPy broadcasting."""
        a_arr = np.array(a).reshape(-1, 1)
        b_arr = np.array(b)
        return a_arr + b_arr
    
    # Test data
    a = list(range(1000))
    b = [list(range(1000))]
    
    # Compare performance
    loop_time = timeit.timeit(lambda: matrix_operations_loops(a, b), number=10)
    broadcast_time = timeit.timeit(lambda: matrix_operations_broadcasting(a, b), number=10)
    
    print(f"\nMatrix Operations:")
    print(f"  Python loops: {loop_time:.6f}s")
    print(f"  NumPy broadcasting: {broadcast_time:.6f}s")
    print(f"  NumPy speedup: {loop_time/broadcast_time:.1f}x")

benchmark_vectorization()
numpy_advanced_optimizations()
```

## Memory Optimization

### Slots and Memory Layout

```python
import sys
from dataclasses import dataclass

class RegularClass:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class SlottedClass:
    __slots__ = ['x', 'y', 'z']
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

@dataclass
class DataClass:
    x: int
    y: int
    z: int

@dataclass
class SlottedDataClass:
    __slots__ = ['x', 'y', 'z']
    x: int
    y: int
    z: int

def compare_memory_usage():
    """Compare memory usage of different class implementations."""
    instances = [
        ("Regular Class", RegularClass(1, 2, 3)),
        ("Slotted Class", SlottedClass(1, 2, 3)),
        ("Data Class", DataClass(1, 2, 3)),
        ("Slotted Data Class", SlottedDataClass(1, 2, 3))
    ]
    
    print("Memory Usage Comparison:")
    for name, instance in instances:
        size = sys.getsizeof(instance)
        if hasattr(instance, '__dict__'):
            size += sys.getsizeof(instance.__dict__)
        print(f"  {name}: {size} bytes")

# Generator vs List memory usage
def memory_efficient_processing():
    """Demonstrate memory-efficient data processing."""
    
    def process_with_list(n):
        """Process data storing all intermediate results."""
        data = [i for i in range(n)]
        squared = [x**2 for x in data]
        filtered = [x for x in squared if x % 2 == 0]
        return sum(filtered)
    
    def process_with_generator(n):
        """Process data using generators."""
        data = range(n)
        squared = (x**2 for x in data)
        filtered = (x for x in squared if x % 2 == 0)
        return sum(filtered)
    
    n = 1000000
    
    # Measure memory usage
    tracemalloc.start()
    result1 = process_with_list(n)
    list_current, list_peak = tracemalloc.get_traced_memory()
    
    tracemalloc.clear_traces()
    result2 = process_with_generator(n)
    gen_current, gen_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\nMemory Efficiency:")
    print(f"  List approach peak: {list_peak / 1024 / 1024:.1f} MB")
    print(f"  Generator approach peak: {gen_peak / 1024 / 1024:.1f} MB")
    print(f"  Memory savings: {(list_peak - gen_peak) / list_peak * 100:.1f}%")
    print(f"  Results match: {result1 == result2}")

compare_memory_usage()
memory_efficient_processing()
```

## Profiling and Monitoring in Production

```python
import psutil
import threading
import time
from collections import defaultdict
from typing import Dict, List

class PerformanceMonitor:
    """Production-ready performance monitoring."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval=1.0):
        """Start background monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                # CPU and memory metrics
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                
                timestamp = time.time()
                self.metrics['cpu_percent'].append((timestamp, cpu_percent))
                self.metrics['memory_rss'].append((timestamp, memory_info.rss))
                self.metrics['memory_vms'].append((timestamp, memory_info.vms))
                
                # Keep only recent metrics (last 1000 points)
                for key in self.metrics:
                    if len(self.metrics[key]) > 1000:
                        self.metrics[key] = self.metrics[key][-1000:]
                
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def get_summary(self) -> Dict:
        """Get performance summary."""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                metric_values = [v[1] for v in values]
                summary[metric_name] = {
                    'current': metric_values[-1],
                    'average': sum(metric_values) / len(metric_values),
                    'max': max(metric_values),
                    'min': min(metric_values)
                }
        
        return summary
    
    def context_manager(self, operation_name):
        """Context manager for operation monitoring."""
        return OperationMonitor(self, operation_name)

class OperationMonitor:
    """Context manager for monitoring specific operations."""
    
    def __init__(self, monitor, operation_name):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        self.start_memory = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        self.start_memory = self.monitor.process.memory_info().rss
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        end_memory = self.monitor.process.memory_info().rss
        
        duration = end_time - self.start_time
        memory_delta = end_memory - self.start_memory
        
        self.monitor.metrics[f'{self.operation_name}_duration'].append(
            (self.start_time, duration)
        )
        self.monitor.metrics[f'{self.operation_name}_memory_delta'].append(
            (self.start_time, memory_delta)
        )

# Example usage
def production_monitoring_example():
    """Example of production performance monitoring."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring(interval=0.1)
    
    try:
        # Simulate various operations
        with monitor.context_manager('data_processing'):
            # Simulate data processing
            data = [i**2 for i in range(100000)]
            result = sum(data)
        
        with monitor.context_manager('file_operations'):
            # Simulate file operations
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w') as f:
                f.write('x' * 1000000)
                f.flush()
        
        time.sleep(2)  # Let monitoring collect data
        
        # Get performance summary
        summary = monitor.get_summary()
        print("Performance Summary:")
        for metric, stats in summary.items():
            print(f"  {metric}:")
            for stat_name, value in stats.items():
                if 'memory' in metric.lower():
                    print(f"    {stat_name}: {value / 1024 / 1024:.1f} MB")
                elif 'duration' in metric.lower():
                    print(f"    {stat_name}: {value:.4f} s")
                else:
                    print(f"    {stat_name}: {value:.2f}")
    
    finally:
        monitor.stop_monitoring()

production_monitoring_example()
```

## Optimization Best Practices

### The Optimization Process

```python
def optimization_checklist():
    """
    Performance Optimization Checklist:
    
    1. MEASURE FIRST
       - Profile your code to find actual bottlenecks
       - Don't optimize based on assumptions
       - Use appropriate profiling tools (cProfile, line_profiler, memory_profiler)
    
    2. SET PERFORMANCE GOALS
       - Define what "fast enough" means
       - Consider user experience requirements
       - Balance performance with maintainability
    
    3. OPTIMIZE IN ORDER OF IMPACT
       - Algorithm complexity (O(n²) → O(n log n))
       - Data structures (list → set for lookups)
       - Built-in functions and libraries
       - Code-level optimizations
    
    4. USE THE RIGHT TOOLS
       - NumPy for numerical computations
       - Pandas for data analysis
       - asyncio for I/O-bound operations
       - multiprocessing for CPU-bound tasks
    
    5. CACHE INTELLIGENTLY
       - Memoize expensive function calls
       - Use appropriate cache sizes
       - Consider cache invalidation strategies
    
    6. MINIMIZE I/O
       - Batch operations when possible
       - Use appropriate buffer sizes
       - Consider async I/O for concurrent operations
    
    7. PROFILE AFTER OPTIMIZATION
       - Verify that optimizations actually helped
       - Watch for regressions in other areas
       - Monitor production performance
    """
    pass

# Common optimization anti-patterns
def optimization_anti_patterns():
    """
    AVOID THESE COMMON MISTAKES:
    
    1. Premature optimization
       - Don't optimize before you have a working solution
       - Don't optimize without measurements
    
    2. Micro-optimizations at the cost of readability
       - Prefer clear code over marginally faster code
       - Document complex optimizations
    
    3. Optimizing the wrong thing
       - Profile to find real bottlenecks
       - Consider the full system, not just one function
    
    4. Ignoring maintenance costs
       - Complex optimizations can be harder to debug
       - Consider long-term code maintenance
    
    5. Not considering trade-offs
       - Memory vs CPU usage
       - Development time vs runtime performance
       - Code complexity vs performance gains
    """
    pass

# Performance testing framework
class PerformanceTester:
    """Framework for systematic performance testing."""
    
    @staticmethod
    def compare_implementations(*implementations, test_data=None, iterations=1000):
        """Compare multiple implementations of the same function."""
        if test_data is None:
            test_data = list(range(1000))
        
        results = {}
        
        for name, func in implementations:
            try:
                # Warmup
                func(test_data)
                
                # Time the function
                start_time = time.perf_counter()
                for _ in range(iterations):
                    result = func(test_data)
                end_time = time.perf_counter()
                
                avg_time = (end_time - start_time) / iterations
                results[name] = {
                    'avg_time': avg_time,
                    'result': result
                }
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results
    
    @staticmethod
    def print_comparison(results):
        """Print formatted comparison results."""
        print("Performance Comparison:")
        print("-" * 50)
        
        fastest_time = min(
            r['avg_time'] for r in results.values() 
            if 'avg_time' in r
        )
        
        for name, result in results.items():
            if 'error' in result:
                print(f"{name:20}: ERROR - {result['error']}")
            else:
                time_ms = result['avg_time'] * 1000
                speedup = result['avg_time'] / fastest_time
                print(f"{name:20}: {time_ms:.4f}ms (x{speedup:.2f})")

# Example usage of performance tester
def example_performance_testing():
    """Example of systematic performance testing."""
    
    def bubble_sort(arr):
        arr = arr.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    def python_sort(arr):
        return sorted(arr)
    
    def numpy_sort(arr):
        return np.sort(arr).tolist()
    
    test_data = list(range(1000, 0, -1))  # Reverse sorted list
    
    tester = PerformanceTester()
    results = tester.compare_implementations(
        ("Bubble Sort", bubble_sort),
        ("Python Sort", python_sort),
        ("NumPy Sort", numpy_sort),
        test_data=test_data,
        iterations=10
    )
    
    tester.print_comparison(results)

example_performance_testing()
```

## Conclusion

Performance optimization is an art that combines measurement, analysis, and strategic thinking. Key principles:

- **Always measure before optimizing** - Profile to find real bottlenecks
- **Choose the right algorithm and data structures** - Often the biggest wins
- **Use appropriate tools** - NumPy, asyncio, multiprocessing for their strengths
- **Consider trade-offs** - Performance vs maintainability vs development time
- **Optimize for your specific use case** - What matters in your application?
- **Monitor production performance** - Optimization is an ongoing process

Remember: premature optimization is the root of all evil, but measured, targeted optimization is essential for building scalable Python applications.

The "Better Python" series has taken us from clean code principles through advanced optimization techniques. Each post builds on the others, creating a comprehensive approach to writing excellent Python code that is readable, maintainable, and performant.

## Practice Exercises

1. Profile a real application and identify its top 3 bottlenecks
2. Optimize a data processing pipeline using appropriate data structures
3. Compare different approaches for a CPU-intensive algorithm
4. Build a monitoring system for production performance tracking

*What performance challenges have you encountered in your Python projects? Which optimization techniques have given you the biggest improvements?*

---

*This concludes the "Better Python" series. Thank you for joining this journey toward writing more effective, elegant Python code. Keep measuring, keep optimizing, and keep learning!*
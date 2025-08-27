---
layout:     post
title:      "Dataclasses vs. NamedTuples vs. Regular Classes: A Practical Guide"
date:       2025-01-06
summary:    When I stopped guessing and started choosing the right tool for structured data in Python
categories: python dataclasses namedtuples design
---

Last week, a junior developer asked me: "Should this be a dataclass, namedtuple, or regular class?"

I realized I'd been answering this question for years without a clear framework. Time to fix that.

## The problem: too many ways to structure data

Python gives us multiple ways to group related data. Each has its place, but the choice isn't always obvious:

```python
# Option 1: Regular dictionary
user = {"name": "Alice", "age": 30, "email": "alice@example.com"}

# Option 2: Named tuple
User = namedtuple("User", ["name", "age", "email"])
user = User("Alice", 30, "alice@example.com")

# Option 3: Dataclass
@dataclass
class User:
    name: str
    age: int
    email: str

# Option 4: Regular class
class User:
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
```

For years, I picked based on mood. Then I started noticing patterns in successful codebases.

## NamedTuples: When immutability matters

I use namedtuples for data that represents a point-in-time snapshot:

```python
from collections import namedtuple

# Perfect for coordinates, measurements, API responses
Point = namedtuple("Point", ["x", "y"])
Temperature = namedtuple("Temperature", ["value", "unit", "timestamp"])

# Great for function returns with multiple values
ProcessResult = namedtuple("ProcessResult", ["success", "message", "data"])

def process_file(filename):
    try:
        data = load_file(filename)
        result = transform_data(data)
        return ProcessResult(True, "Success", result)
    except Exception as e:
        return ProcessResult(False, str(e), None)
```

**Use namedtuples when:**
- Data shouldn't change after creation
- You need tuple-like behavior (unpacking, indexing)
- Memory efficiency matters (they're more compact than classes)
- You're replacing tuples but want named access

**Don't use them when:**
- You need methods beyond simple data access
- Data will be modified frequently
- You need default values (though `typing.NamedTuple` helps)

## Dataclasses: The sweet spot for most use cases

Dataclasses hit the sweet spot between simplicity and functionality:

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Task:
    title: str
    description: str
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    completed: bool = False
    assigned_to: Optional[str] = None

# Free methods: __init__, __repr__, __eq__
task = Task("Fix bug", "Resolve the login issue")
print(task)  # Task(title='Fix bug', description='Resolve the login issue', ...)

# Easy modification
task.completed = True
task.tags.append("urgent")
```

I use dataclasses for:

**Configuration objects:**
```python
@dataclass
class DatabaseConfig:
    host: str
    port: int = 5432
    database: str = "app"
    username: str = "user"
    password: str = field(repr=False)  # Don't print passwords
    pool_size: int = 10
```

**API data models:**
```python
@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_api(cls, data: dict) -> 'User':
        return cls(**data)
```

**Use dataclasses when:**
- You need mutable data with structure
- You want automatic `__init__`, `__repr__`, `__eq__`
- Type hints are important
- You might add methods later
- Default values and field customization matter

## Regular classes: When you need behavior

Regular classes are for objects that *do* things, not just hold data:

```python
class WorkflowEngine:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
        self.task_queue = []
        
    def connect(self):
        self.connection = create_connection(self.config)
        
    def add_task(self, task: Task):
        self.task_queue.append(task)
        
    def execute(self):
        for task in self.task_queue:
            result = self._execute_task(task)
            self._log_result(result)
```

**Use regular classes when:**
- The object encapsulates behavior, not just data
- You need complex initialization logic
- State management is important
- You're implementing interfaces or protocols

## The decision framework I use

Here's the decision tree I've developed:

1. **Is this data immutable after creation?** → NamedTuple
2. **Does this object need methods beyond data access?** → Regular Class
3. **Is this primarily structured data with simple behavior?** → Dataclass
4. **Am I replacing a dictionary or tuple?** → Dataclass or NamedTuple

## Real examples from production code

**Configuration that never changes (NamedTuple):**
```python
ServerConfig = namedtuple("ServerConfig", [
    "host", "port", "ssl_cert", "ssl_key", "workers"
])

config = ServerConfig("0.0.0.0", 8080, "cert.pem", "key.pem", 4)
```

**Data that gets modified (Dataclass):**
```python
@dataclass
class WorkflowRun:
    id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
```

**Object with complex behavior (Regular Class):**
```python
class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pending_tasks = []
        
    def schedule(self, task: callable) -> Future:
        return self.executor.submit(task)
```

## The mistake I see most often

The biggest mistake? Using dictionaries for structured data:

```python
# Don't do this
user = {"name": "Alice", "age": 30, "email": "alice@example.com"}
users.append(user)

# Do this instead
@dataclass
class User:
    name: str
    age: int
    email: str

users.append(User("Alice", 30, "alice@example.com"))
```

Dictionaries are for unknown or dynamic structure. When you know the fields at design time, use a proper data structure.

## The bottom line

- **NamedTuple**: Immutable data, point-in-time snapshots
- **Dataclass**: Structured, mutable data with minimal behavior
- **Regular Class**: Objects that encapsulate both data and behavior

Choose based on what the data represents and how it will be used. Your future self will thank you for the clarity.
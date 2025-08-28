---
layout: post
title: "Better Python: Data Classes and Modern Object-Oriented Design"
date: 2025-03-05
summary: "Discover how data classes, properties, and modern OOP patterns make Python code more maintainable, readable, and Pythonic."
categories: python programming dataclasses oop design-patterns better-python
---

# Modern Python Object-Oriented Design

Python's approach to object-oriented programming has evolved significantly. With data classes, properties, descriptors, and modern design patterns, we can write more expressive, maintainable code that clearly communicates intent and reduces boilerplate.

## Data Classes: The Modern Way

Data classes, introduced in Python 3.7, dramatically reduce boilerplate for classes that primarily store data:

```python
# Traditional class - lots of boilerplate
class PersonOld:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email
    
    def __repr__(self):
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"
    
    def __eq__(self, other):
        if not isinstance(other, PersonOld):
            return False
        return (self.name, self.age, self.email) == (other.name, other.age, other.email)

# Data class - clean and concise
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str

# Both classes provide the same functionality:
person1 = Person("Alice", 30, "alice@example.com")
person2 = Person("Alice", 30, "alice@example.com")
print(person1)  # Person(name='Alice', age=30, email='alice@example.com')
print(person1 == person2)  # True
```

### Advanced Data Class Features

```python
from dataclasses import dataclass, field, InitVar
from typing import List, Optional
from datetime import datetime
import uuid

@dataclass(frozen=True, order=True)  # Immutable and sortable
class Product:
    name: str
    price: float
    category: str
    sku: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Exclude from repr and comparison
    _internal_id: int = field(default=0, repr=False, compare=False)
    
    def __post_init__(self):
        # Validation can happen here
        if self.price < 0:
            raise ValueError("Price cannot be negative")

@dataclass
class ShoppingCart:
    customer_id: str
    items: List[Product] = field(default_factory=list)
    
    # Computed property
    @property
    def total_price(self) -> float:
        return sum(item.price for item in self.items)
    
    @property
    def item_count(self) -> int:
        return len(self.items)
    
    def add_item(self, product: Product) -> None:
        self.items.append(product)
    
    def remove_item(self, sku: str) -> bool:
        for i, item in enumerate(self.items):
            if item.sku == sku:
                del self.items[i]
                return True
        return False

# Usage
products = [
    Product("Laptop", 999.99, "Electronics"),
    Product("Mouse", 29.99, "Electronics"),
    Product("Book", 15.99, "Books")
]

cart = ShoppingCart("customer123")
for product in products:
    cart.add_item(product)

print(f"Cart total: ${cart.total_price:.2f}")
print(f"Items: {cart.item_count}")
```

### Data Classes with Inheritance

```python
@dataclass
class Vehicle:
    make: str
    model: str
    year: int
    
    @property
    def age(self) -> int:
        from datetime import datetime
        return datetime.now().year - self.year

@dataclass
class Car(Vehicle):
    doors: int = 4
    fuel_type: str = "gasoline"
    
    def start_engine(self) -> str:
        return f"Starting {self.make} {self.model} engine"

@dataclass
class ElectricCar(Car):
    battery_capacity: float = 0.0  # kWh
    range_miles: int = 0
    fuel_type: str = field(default="electric", init=False)  # Override parent
    
    def charge(self, kwh: float) -> str:
        return f"Charging {kwh}kWh into {self.battery_capacity}kWh battery"

# Usage
tesla = ElectricCar("Tesla", "Model 3", 2023, doors=4, battery_capacity=75.0, range_miles=350)
print(tesla.start_engine())
print(tesla.charge(50.0))
print(f"Car age: {tesla.age} years")
```

## Properties and Descriptors

### Properties for Computed Values and Validation

```python
class Temperature:
    def __init__(self, celsius: float = 0):
        self._celsius = celsius
    
    @property
    def celsius(self) -> float:
        return self._celsius
    
    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self) -> float:
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15
    
    def __repr__(self):
        return f"Temperature({self._celsius}°C)"

# Usage
temp = Temperature(25)
print(f"Celsius: {temp.celsius}")      # 25
print(f"Fahrenheit: {temp.fahrenheit}") # 77.0
print(f"Kelvin: {temp.kelvin}")        # 298.15

temp.fahrenheit = 100
print(f"Celsius: {temp.celsius}")      # 37.777...
```

### Custom Descriptors

```python
class ValidatedAttribute:
    def __init__(self, validator, default=None):
        self.validator = validator
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, self.default)
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        setattr(obj, self.name, value)

class PositiveNumber:
    def __init__(self, default=0):
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, self.default)
    
    def __set__(self, obj, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{self.name[1:]} must be a positive number")
        setattr(obj, self.name, value)

class BankAccount:
    balance = PositiveNumber(default=0.0)
    interest_rate = ValidatedAttribute(
        validator=lambda x: isinstance(x, float) and 0 <= x <= 1,
        default=0.02
    )
    
    def __init__(self, account_number: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self.balance = initial_balance
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
    
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

# Usage
account = BankAccount("12345", 1000.0)
account.deposit(500.0)
print(f"Balance: ${account.balance}")

try:
    account.balance = -100  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

## Modern Class Design Patterns

### Builder Pattern with Method Chaining

```python
from typing import Optional, Dict, Any

class QueryBuilder:
    def __init__(self):
        self._select_fields: List[str] = []
        self._from_table: Optional[str] = None
        self._where_conditions: List[str] = []
        self._joins: List[str] = []
        self._order_by: List[str] = []
        self._limit_value: Optional[int] = None
        self._params: Dict[str, Any] = {}
    
    def select(self, *fields: str) -> 'QueryBuilder':
        self._select_fields.extend(fields)
        return self
    
    def from_table(self, table: str) -> 'QueryBuilder':
        self._from_table = table
        return self
    
    def where(self, condition: str, **params) -> 'QueryBuilder':
        self._where_conditions.append(condition)
        self._params.update(params)
        return self
    
    def join(self, table: str, on_condition: str) -> 'QueryBuilder':
        self._joins.append(f"JOIN {table} ON {on_condition}")
        return self
    
    def order_by(self, field: str, direction: str = "ASC") -> 'QueryBuilder':
        self._order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        self._limit_value = count
        return self
    
    def build(self) -> str:
        if not self._from_table:
            raise ValueError("FROM table is required")
        
        query_parts = []
        
        # SELECT
        if self._select_fields:
            query_parts.append(f"SELECT {', '.join(self._select_fields)}")
        else:
            query_parts.append("SELECT *")
        
        # FROM
        query_parts.append(f"FROM {self._from_table}")
        
        # JOINs
        query_parts.extend(self._joins)
        
        # WHERE
        if self._where_conditions:
            query_parts.append(f"WHERE {' AND '.join(self._where_conditions)}")
        
        # ORDER BY
        if self._order_by:
            query_parts.append(f"ORDER BY {', '.join(self._order_by)}")
        
        # LIMIT
        if self._limit_value:
            query_parts.append(f"LIMIT {self._limit_value}")
        
        return " ".join(query_parts)

# Usage
query = (QueryBuilder()
         .select("users.name", "users.email", "profiles.bio")
         .from_table("users")
         .join("profiles", "users.id = profiles.user_id")
         .where("users.active = :active", active=True)
         .where("users.created_at > :date", date="2023-01-01")
         .order_by("users.name")
         .limit(10)
         .build())

print(query)
```

### Factory Pattern with Registration

```python
from abc import ABC, abstractmethod
from typing import Dict, Type, Any

class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class CSVProcessor(DataProcessor):
    def process(self, data: str) -> list:
        lines = data.strip().split('\n')
        return [line.split(',') for line in lines]

class JSONProcessor(DataProcessor):
    def process(self, data: str) -> dict:
        import json
        return json.loads(data)

class XMLProcessor(DataProcessor):
    def process(self, data: str) -> dict:
        # Simplified XML processing
        return {"xml_data": data}

class ProcessorFactory:
    _processors: Dict[str, Type[DataProcessor]] = {}
    
    @classmethod
    def register(cls, format_type: str, processor_class: Type[DataProcessor]):
        """Register a processor for a specific format."""
        cls._processors[format_type.lower()] = processor_class
    
    @classmethod
    def create_processor(cls, format_type: str) -> DataProcessor:
        """Create a processor instance for the given format."""
        processor_class = cls._processors.get(format_type.lower())
        if not processor_class:
            raise ValueError(f"No processor registered for format: {format_type}")
        return processor_class()
    
    @classmethod
    def get_supported_formats(cls) -> list:
        """Get list of supported formats."""
        return list(cls._processors.keys())

# Register processors
ProcessorFactory.register("csv", CSVProcessor)
ProcessorFactory.register("json", JSONProcessor)
ProcessorFactory.register("xml", XMLProcessor)

# Decorator for automatic registration
def register_processor(format_type: str):
    def decorator(cls):
        ProcessorFactory.register(format_type, cls)
        return cls
    return decorator

@register_processor("yaml")
class YAMLProcessor(DataProcessor):
    def process(self, data: str) -> dict:
        # Simplified YAML processing
        return {"yaml_data": data}

# Usage
def process_data(data: str, format_type: str):
    processor = ProcessorFactory.create_processor(format_type)
    return processor.process(data)

csv_data = "name,age\nAlice,30\nBob,25"
result = process_data(csv_data, "csv")
print(result)

print(f"Supported formats: {ProcessorFactory.get_supported_formats()}")
```

### Singleton with Thread Safety

```python
import threading
from typing import Optional

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, host: str = "localhost", port: int = 5432):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.host = host
            self.port = port
            self.connection = None
            self.initialized = True
    
    def connect(self):
        if not self.connection:
            print(f"Connecting to {self.host}:{self.port}")
            self.connection = f"Connected to {self.host}:{self.port}"
        return self.connection
    
    def disconnect(self):
        if self.connection:
            print("Disconnecting...")
            self.connection = None

# Better approach: Using module-level instance
class _DatabaseManager:
    def __init__(self):
        self._connections = {}
        self._lock = threading.Lock()
    
    def get_connection(self, name: str = "default", **kwargs):
        if name not in self._connections:
            with self._lock:
                if name not in self._connections:
                    self._connections[name] = DatabaseConnection(**kwargs)
        return self._connections[name]

# Module-level instance
db_manager = _DatabaseManager()

# Usage
db1 = db_manager.get_connection()
db2 = db_manager.get_connection()
print(db1 is db2)  # True - same instance
```

## Composition Over Inheritance

```python
from abc import ABC, abstractmethod
from typing import List

# Instead of deep inheritance hierarchies, use composition

class Flyable(ABC):
    @abstractmethod
    def fly(self) -> str:
        pass

class Swimmable(ABC):
    @abstractmethod
    def swim(self) -> str:
        pass

class Walkable(ABC):
    @abstractmethod
    def walk(self) -> str:
        pass

# Concrete implementations
class WingFlight(Flyable):
    def fly(self) -> str:
        return "Flying with wings"

class JetPropulsion(Flyable):
    def fly(self) -> str:
        return "Flying with jet propulsion"

class LegSwimming(Swimmable):
    def swim(self) -> str:
        return "Swimming with legs"

class FinSwimming(Swimmable):
    def swim(self) -> str:
        return "Swimming with fins"

class LegWalking(Walkable):
    def walk(self) -> str:
        return "Walking on legs"

# Compose behaviors
@dataclass
class Animal:
    name: str
    species: str
    _abilities: List[object] = field(default_factory=list)
    
    def add_ability(self, ability):
        self._abilities.append(ability)
        return self
    
    def can_fly(self) -> bool:
        return any(isinstance(ability, Flyable) for ability in self._abilities)
    
    def can_swim(self) -> bool:
        return any(isinstance(ability, Swimmable) for ability in self._abilities)
    
    def can_walk(self) -> bool:
        return any(isinstance(ability, Walkable) for ability in self._abilities)
    
    def fly(self) -> str:
        for ability in self._abilities:
            if isinstance(ability, Flyable):
                return f"{self.name} is {ability.fly().lower()}"
        return f"{self.name} cannot fly"
    
    def swim(self) -> str:
        for ability in self._abilities:
            if isinstance(ability, Swimmable):
                return f"{self.name} is {ability.swim().lower()}"
        return f"{self.name} cannot swim"
    
    def walk(self) -> str:
        for ability in self._abilities:
            if isinstance(ability, Walkable):
                return f"{self.name} is {ability.walk().lower()}"
        return f"{self.name} cannot walk"

# Create animals with different ability combinations
duck = (Animal("Donald", "Duck")
        .add_ability(WingFlight())
        .add_ability(LegSwimming())
        .add_ability(LegWalking()))

fish = (Animal("Nemo", "Clownfish")
        .add_ability(FinSwimming()))

penguin = (Animal("Tux", "Penguin")
           .add_ability(LegSwimming())
           .add_ability(LegWalking()))

airplane = (Animal("Boeing", "Aircraft")
            .add_ability(JetPropulsion()))

# Test abilities
for animal in [duck, fish, penguin, airplane]:
    print(f"\n{animal.name} ({animal.species}):")
    print(f"  Fly: {animal.fly()}")
    print(f"  Swim: {animal.swim()}")
    print(f"  Walk: {animal.walk()}")
```

## Modern Python Class Features

### `__slots__` for Memory Optimization

```python
@dataclass
class RegularPoint:
    x: float
    y: float

@dataclass
class SlottedPoint:
    __slots__ = ['x', 'y']
    x: float
    y: float

# Memory comparison
import sys

regular = RegularPoint(1.0, 2.0)
slotted = SlottedPoint(1.0, 2.0)

print(f"Regular point size: {sys.getsizeof(regular)} bytes")
print(f"Slotted point size: {sys.getsizeof(slotted)} bytes")

# Performance implications
import timeit

def test_regular():
    p = RegularPoint(1.0, 2.0)
    return p.x + p.y

def test_slotted():
    p = SlottedPoint(1.0, 2.0)
    return p.x + p.y

regular_time = timeit.timeit(test_regular, number=1000000)
slotted_time = timeit.timeit(test_slotted, number=1000000)

print(f"Regular access time: {regular_time:.4f}s")
print(f"Slotted access time: {slotted_time:.4f}s")
```

### Context Manager Classes

```python
class ManagedResource:
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.resource = None
    
    def __enter__(self):
        print(f"Acquiring {self.resource_name}")
        self.resource = f"Resource: {self.resource_name}"
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Releasing {self.resource_name}")
        if exc_type:
            print(f"Exception occurred: {exc_val}")
        self.resource = None
        return False  # Don't suppress exceptions

# Usage
with ManagedResource("Database Connection") as resource:
    print(f"Using {resource}")
    # Automatic cleanup happens here
```

### Callable Classes

```python
@dataclass
class Accumulator:
    total: float = 0.0
    
    def __call__(self, value: float) -> float:
        self.total += value
        return self.total
    
    def reset(self) -> None:
        self.total = 0.0

# Usage as a callable
acc = Accumulator()
print(acc(10))    # 10.0
print(acc(5))     # 15.0
print(acc(3))     # 18.0

# Function factories
def create_multiplier(factor: float):
    @dataclass
    class Multiplier:
        factor: float
        
        def __call__(self, value: float) -> float:
            return value * self.factor
    
    return Multiplier(factor)

double = create_multiplier(2.0)
triple = create_multiplier(3.0)

print(double(5))  # 10.0
print(triple(4))  # 12.0
```

## Testing Object-Oriented Code

```python
import pytest
from unittest.mock import Mock, patch

class UserService:
    def __init__(self, database, email_service):
        self.database = database
        self.email_service = email_service
    
    def create_user(self, username: str, email: str) -> dict:
        # Check if user exists
        if self.database.get_user(username):
            raise ValueError(f"User {username} already exists")
        
        # Create user
        user = {
            'username': username,
            'email': email,
            'id': self.database.create_user(username, email)
        }
        
        # Send welcome email
        self.email_service.send_welcome_email(email, username)
        
        return user

# Test with dependency injection
def test_user_service():
    # Create mocks
    mock_database = Mock()
    mock_email_service = Mock()
    
    # Configure mocks
    mock_database.get_user.return_value = None  # User doesn't exist
    mock_database.create_user.return_value = 123
    
    # Create service with mocked dependencies
    service = UserService(mock_database, mock_email_service)
    
    # Test user creation
    user = service.create_user("alice", "alice@example.com")
    
    # Verify behavior
    assert user['username'] == "alice"
    assert user['id'] == 123
    
    mock_database.get_user.assert_called_once_with("alice")
    mock_database.create_user.assert_called_once_with("alice", "alice@example.com")
    mock_email_service.send_welcome_email.assert_called_once_with("alice@example.com", "alice")

# Test data classes
def test_product_dataclass():
    product = Product("Laptop", 999.99, "Electronics")
    
    # Test immutability (if frozen=True)
    with pytest.raises(AttributeError):
        product.name = "Desktop"  # Should fail if frozen
    
    # Test validation
    with pytest.raises(ValueError):
        Product("Invalid", -100, "Electronics")  # Negative price
```

## Best Practices

### 1. Favor Composition Over Inheritance

```python
# Instead of deep inheritance
class Animal:
    pass

class Mammal(Animal):
    pass

class Dog(Mammal):
    pass

class WorkingDog(Dog):
    pass

# Use composition and interfaces
class Animal:
    def __init__(self, behaviors=None):
        self.behaviors = behaviors or []

# More flexible and testable
```

### 2. Use Data Classes for Data Containers

```python
# Good: Clear data structure
@dataclass
class User:
    username: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)

# Avoid: Classes that are just bags of data without data class
class UserOld:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        # ... lots of boilerplate
```

### 3. Implement `__str__` and `__repr__` Thoughtfully

```python
@dataclass
class Point:
    x: float
    y: float
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"  # Human-readable
    
    # __repr__ is auto-generated by dataclass for debugging
```

### 4. Use Properties for Computed Values and Validation

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius
    
    @property
    def radius(self) -> float:
        return self._radius
    
    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Radius must be positive")
        self._radius = value
    
    @property
    def area(self) -> float:
        return 3.14159 * self._radius ** 2
```

## Conclusion

Modern Python object-oriented design emphasizes clarity, simplicity, and maintainability. Key principles:

- **Use data classes for data-focused classes**
- **Favor composition over deep inheritance**
- **Implement proper encapsulation with properties**
- **Design for dependency injection and testability**
- **Use descriptors for reusable validation logic**
- **Apply design patterns judiciously**

These patterns make your code more readable, maintainable, and Pythonic while leveraging modern language features effectively.

In our next post, we'll explore testing strategies and best practices that ensure your well-designed code works correctly and remains reliable.

## Practice Exercises

1. Convert a traditional class to use data classes
2. Implement a flexible plugin system using composition
3. Create a custom descriptor for validation
4. Design a builder pattern for complex object creation

*How has modern OOP changed your Python code structure? What patterns do you find most useful?*
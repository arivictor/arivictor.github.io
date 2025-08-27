---
layout: post
title: "Better Python: Type Hints and Static Analysis"
date: 2025-02-19
summary: "Discover how type hints make your Python code more maintainable, self-documenting, and error-resistant. Learn advanced typing patterns and static analysis tools."
categories: python programming type-hints mypy static-analysis better-python
---

# Making Python Code Self-Documenting

Type hints are one of Python's most transformative features, introduced in Python 3.5. They make code more readable, catch errors early, and enable powerful tooling. While Python remains dynamically typed at runtime, type hints provide static analysis benefits without sacrificing flexibility.

## Why Type Hints Matter

```python
# Without type hints - unclear what this function expects and returns
def process_data(data, config, callback):
    result = []
    for item in data:
        if config.enabled:
            processed = callback(item, config.multiplier)
            result.append(processed)
    return result

# With type hints - immediately clear what's expected
from typing import List, Callable, Any

def process_data(
    data: List[Any], 
    config: ProcessingConfig, 
    callback: Callable[[Any, float], Any]
) -> List[Any]:
    result = []
    for item in data:
        if config.enabled:
            processed = callback(item, config.multiplier)
            result.append(processed)
    return result
```

## Basic Type Hints

### Built-in Types

```python
# Basic types
name: str = "Alice"
age: int = 30
height: float = 1.75
is_active: bool = True

# Collections
numbers: list = [1, 2, 3]
coordinates: tuple = (10.0, 20.0)
unique_items: set = {1, 2, 3}
mapping: dict = {"key": "value"}

# Functions
def greet(name: str) -> str:
    return f"Hello, {name}!"

def calculate_area(length: float, width: float) -> float:
    return length * width

# No return value
def log_message(message: str) -> None:
    print(f"LOG: {message}")
```

### Generic Types

```python
from typing import List, Dict, Set, Tuple, Optional, Union

# Parameterized types
names: List[str] = ["Alice", "Bob", "Charlie"]
scores: Dict[str, int] = {"Alice": 95, "Bob": 87}
unique_ids: Set[int] = {1, 2, 3, 4}
coordinates: Tuple[float, float] = (10.5, 20.3)

# Optional types (Union with None)
middle_name: Optional[str] = None  # Same as Union[str, None]

# Union types
def process_id(user_id: Union[int, str]) -> str:
    return str(user_id)

# Variable length tuples
def calculate_average(*numbers: float) -> float:
    return sum(numbers) / len(numbers)

scores: Tuple[int, ...] = (85, 92, 78, 96)  # Variable length
```

## Advanced Type Hints

### Type Aliases

```python
from typing import Dict, List, Union

# Create meaningful type aliases
UserId = int
Username = str
UserData = Dict[str, Union[str, int, bool]]
UserList = List[UserData]

def get_user(user_id: UserId) -> Optional[UserData]:
    # Implementation here
    pass

def filter_users(users: UserList, active_only: bool = True) -> UserList:
    return [user for user in users if not active_only or user.get('active', False)]
```

### Callable Types

```python
from typing import Callable, Any

# Function that takes two ints and returns an int
BinaryOp = Callable[[int, int], int]

def apply_operation(a: int, b: int, operation: BinaryOp) -> int:
    return operation(a, b)

# Usage
def add(x: int, y: int) -> int:
    return x + y

result = apply_operation(5, 3, add)

# More complex callable
Validator = Callable[[Any], bool]
Transformer = Callable[[Any], Any]

def process_items(
    items: List[Any], 
    validator: Validator, 
    transformer: Transformer
) -> List[Any]:
    return [transformer(item) for item in items if validator(item)]
```

### Generic Classes

```python
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> Optional[T]:
        if self._items:
            return self._items.pop()
        return None
    
    def peek(self) -> Optional[T]:
        if self._items:
            return self._items[-1]
        return None

# Usage with type checking
string_stack: Stack[str] = Stack()
string_stack.push("hello")
string_stack.push("world")

number_stack: Stack[int] = Stack()
number_stack.push(42)
```

### Protocol Classes (Structural Typing)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def __init__(self, radius: float):
        self.radius = radius
    
    def draw(self) -> None:
        print(f"Drawing circle with radius {self.radius}")

class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def draw(self) -> None:
        print(f"Drawing rectangle {self.width}x{self.height}")

def render_shape(shape: Drawable) -> None:
    shape.draw()

# Both work because they implement the Protocol
render_shape(Circle(5.0))
render_shape(Rectangle(10.0, 8.0))
```

## Data Classes with Type Hints

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    id: int
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class UserProfile:
    user: User
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    def get_display_name(self) -> str:
        return self.user.username.title()

# Usage
user = User(id=1, username="alice", email="alice@example.com")
profile = UserProfile(user=user, bio="Python developer")
```

## Type Checking with mypy

### Installing and Running mypy

```bash
pip install mypy

# Check a single file
mypy script.py

# Check entire project
mypy src/

# Generate HTML report
mypy --html-report mypy-report src/
```

### mypy Configuration

Create a `mypy.ini` file:

```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

# Per-module options
[mypy-requests.*]
ignore_missing_imports = True

[mypy-external_lib.*]
ignore_missing_imports = True
```

### Common mypy Patterns

```python
from typing import TYPE_CHECKING

# Avoid circular imports in type checking
if TYPE_CHECKING:
    from .models import User

def process_user(user: 'User') -> str:  # Forward reference
    return user.username

# Type ignore comments for specific issues
result = some_complex_operation()  # type: ignore[attr-defined]

# Cast types when you know better than mypy
from typing import cast
value = cast(int, some_dynamic_value)

# Reveal types for debugging
reveal_type(some_variable)  # mypy will show the inferred type
```

## Advanced Typing Patterns

### Literal Types

```python
from typing import Literal

Color = Literal["red", "green", "blue"]
Environment = Literal["development", "staging", "production"]

def set_color(color: Color) -> None:
    print(f"Setting color to {color}")

def configure_app(env: Environment) -> None:
    if env == "development":
        enable_debug_mode()
    elif env == "production":
        enable_performance_optimizations()

# Usage
set_color("red")     # ✓ Valid
set_color("purple")  # ✗ mypy error
```

### TypedDict

```python
from typing import TypedDict, Optional

class PersonDict(TypedDict):
    name: str
    age: int
    email: Optional[str]

class PersonDictTotal(TypedDict, total=False):
    name: str      # Required
    age: int       # Required
    phone: str     # Optional because total=False

def process_person(person: PersonDict) -> str:
    name = person["name"]  # mypy knows this exists
    age = person["age"]    # mypy knows this exists
    email = person.get("email", "No email")  # Safely handle optional
    return f"{name} ({age}): {email}"

# Usage
person: PersonDict = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}
```

### Overloads

```python
from typing import overload, Union

@overload
def process_data(data: str) -> str: ...

@overload 
def process_data(data: int) -> int: ...

@overload
def process_data(data: list) -> list: ...

def process_data(data: Union[str, int, list]) -> Union[str, int, list]:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, int):
        return data * 2
    elif isinstance(data, list):
        return sorted(data)
    else:
        raise TypeError(f"Unsupported type: {type(data)}")

# mypy understands the return type based on input
result1 = process_data("hello")    # Type: str
result2 = process_data(42)         # Type: int
result3 = process_data([3, 1, 2])  # Type: list
```

### NewType

```python
from typing import NewType

# Create distinct types for better type safety
UserId = NewType('UserId', int)
ProductId = NewType('ProductId', int)

def get_user(user_id: UserId) -> User:
    # Implementation
    pass

def get_product(product_id: ProductId) -> Product:
    # Implementation  
    pass

# Usage
user_id = UserId(123)
product_id = ProductId(456)

user = get_user(user_id)       # ✓ Correct
user = get_user(product_id)    # ✗ mypy error - type mismatch
```

## Real-World Examples

### API Client with Full Type Safety

```python
from typing import TypeVar, Generic, Dict, Any, Optional, Union
from dataclasses import dataclass
import requests

T = TypeVar('T')

@dataclass
class APIResponse(Generic[T]):
    data: T
    status_code: int
    headers: Dict[str, str]

class APIError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

@dataclass
class User:
    id: int
    name: str
    email: str

@dataclass
class Product:
    id: int
    name: str
    price: float

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if not response.ok:
            raise APIError(f"API request failed: {response.text}", response.status_code)
        
        return response
    
    def get_user(self, user_id: int) -> APIResponse[User]:
        response = self._request('GET', f'/users/{user_id}')
        user_data = response.json()
        user = User(**user_data)
        
        return APIResponse(
            data=user,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    def get_products(self, category: Optional[str] = None) -> APIResponse[List[Product]]:
        params = {'category': category} if category else {}
        response = self._request('GET', '/products', params=params)
        
        products_data = response.json()
        products = [Product(**item) for item in products_data]
        
        return APIResponse(
            data=products,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

# Usage with full type safety
client = APIClient("https://api.example.com", "your-api-key")

user_response = client.get_user(123)
user = user_response.data  # mypy knows this is a User
print(user.name)           # mypy knows User has a name attribute

products_response = client.get_products("electronics")
products = products_response.data  # mypy knows this is List[Product]
for product in products:           # mypy knows product is a Product
    print(f"{product.name}: ${product.price}")
```

### Configuration Management

```python
from typing import Dict, Any, Type, TypeVar, get_type_hints
from dataclasses import dataclass, field
import os
import json

T = TypeVar('T')

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "user"
    password: str = ""

@dataclass
class CacheConfig:
    enabled: bool = True
    ttl: int = 3600
    max_size: int = 1000

@dataclass
class AppConfig:
    debug: bool = False
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    api_keys: Dict[str, str] = field(default_factory=dict)

class ConfigLoader:
    @staticmethod
    def from_env(config_class: Type[T]) -> T:
        """Load configuration from environment variables."""
        hints = get_type_hints(config_class)
        kwargs = {}
        
        for field_name, field_type in hints.items():
            env_var = f"{config_class.__name__.upper()}_{field_name.upper()}"
            env_value = os.getenv(env_var)
            
            if env_value is not None:
                if field_type == bool:
                    kwargs[field_name] = env_value.lower() in ('true', '1', 'yes')
                elif field_type == int:
                    kwargs[field_name] = int(env_value)
                elif field_type == float:
                    kwargs[field_name] = float(env_value)
                else:
                    kwargs[field_name] = env_value
        
        return config_class(**kwargs)
    
    @staticmethod
    def from_file(config_class: Type[T], filename: str) -> T:
        """Load configuration from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return config_class(**data)

# Usage
config = ConfigLoader.from_env(AppConfig)
db_config = ConfigLoader.from_env(DatabaseConfig)
```

## Integration with IDEs and Tools

### VS Code Integration

```json
// .vscode/settings.json
{
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.910
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### Type Stubs

```python
# For libraries without type hints, install type stubs
pip install types-requests
pip install types-redis
pip install types-pyyaml

# Or create your own stub files
# external_lib.pyi
def some_function(param: str) -> int: ...

class SomeClass:
    def method(self, value: float) -> bool: ...
```

## Gradual Typing Strategy

### Adding Types to Existing Code

```python
# Start with function signatures
def process_user_data(data):  # type: ignore
    # Function body unchanged
    pass

# Then add basic types
def process_user_data(data: dict) -> dict:
    # Function body unchanged
    pass

# Finally, add specific types
def process_user_data(data: Dict[str, Any]) -> UserData:
    # Function body unchanged
    pass
```

### Type Comments for Older Python

```python
from typing import List, Dict

# For Python < 3.6, use type comments
def process_items(items, config):
    # type: (List[str], Dict[str, Any]) -> List[str]
    result = []  # type: List[str]
    for item in items:
        if config.get('enabled', True):
            result.append(item.upper())
    return result
```

## Best Practices

### 1. Start Simple, Add Complexity Gradually

```python
# Start with basic types
def calculate_total(prices: list) -> float:
    return sum(prices)

# Then make them more specific
def calculate_total(prices: List[float]) -> float:
    return sum(prices)

# Add constraints where helpful
def calculate_total(prices: List[float]) -> float:
    if not prices:
        return 0.0
    return sum(prices)
```

### 2. Use Type Aliases for Complex Types

```python
# Instead of repeating complex types
JSONDict = Dict[str, Any]
APIResponse = Dict[str, Union[str, int, List[JSONDict]]]

def process_api_response(response: APIResponse) -> List[str]:
    # Much clearer than the full type annotation
    pass
```

### 3. Leverage Protocols for Flexibility

```python
from typing import Protocol

class Serializable(Protocol):
    def serialize(self) -> Dict[str, Any]: ...

def save_to_database(obj: Serializable) -> None:
    data = obj.serialize()
    # Save data to database
```

### 4. Document Complex Type Relationships

```python
from typing import TypeVar, Callable

Input = TypeVar('Input')
Output = TypeVar('Output')
Processor = Callable[[Input], Output]

def pipeline(
    data: Input, 
    *processors: Processor[Input, Input]  # Each processor transforms Input to Input
) -> Input:
    """Apply a series of processors to data."""
    result = data
    for processor in processors:
        result = processor(result)
    return result
```

## Common Pitfalls and Solutions

### 1. Mutable Default Arguments

```python
from typing import List, Optional

# Problematic
def add_item(items: List[str] = []) -> List[str]:  # mypy error
    items.append("new")
    return items

# Solution
def add_item(items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append("new")
    return items
```

### 2. Circular Imports

```python
# models/user.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .order import Order

class User:
    def get_orders(self) -> List['Order']:  # Forward reference
        pass
```

### 3. Any vs Generic

```python
from typing import Any, TypeVar, Generic

T = TypeVar('T')

# Less helpful - loses type information
def process_data(data: Any) -> Any:
    return data

# Better - preserves type information  
def process_data(data: T) -> T:
    return data
```

## Conclusion

Type hints transform Python development by making code more readable, catching errors early, and enabling powerful tooling. They represent Python's evolution toward better developer experience while maintaining its dynamic nature.

Key benefits:
- **Self-documenting code**: Types serve as inline documentation
- **Early error detection**: Catch bugs before runtime
- **Better IDE support**: Enhanced autocompletion and refactoring
- **Improved maintainability**: Easier to understand and modify code
- **Team productivity**: Clearer contracts between functions and modules

Start gradually, focus on public APIs first, and let static analysis tools guide your typing journey.

In our next post, we'll explore async/await and concurrent programming—essential patterns for building high-performance Python applications.

## Practice Exercises

1. Add type hints to an existing Python module
2. Create a generic data structure with full type safety
3. Design a Protocol for a plugin system
4. Set up mypy for a project with custom configuration

*How has adding type hints changed your development workflow? What challenges have you encountered?*
---
layout: course
title: "DDD Workshop Part 2: Entities and Value Objects"
part: "Part 2 of 5"
duration: "90 minutes"
prev_course: "/courses/01-event-storming-contexts/"
prev_title: "Event Storming and Contexts"
next_course: "/courses/03-repositories-aggregates/"
next_title: "Repositories and Aggregates"
order: 2
---

# Entities and Value Objects: The Building Blocks of Domain Models

**Goal:** Transform the ubiquitous language discovered in event storming into robust, expressive code that accurately represents business concepts and enforces business rules.

## Introduction: From Language to Code

In Part 1, we discovered the language of our domain through events and contexts. Now we face a critical challenge: **How do we represent business concepts in code without losing their meaning?**

Most traditional approaches fall into the trap of **anemic domain models** - classes that are little more than data containers with getters and setters. This approach fails because:

- **Business logic spreads throughout the application** instead of being centralized
- **Domain concepts become unclear** and lose their expressiveness
- **Business rules are easy to bypass** or implement inconsistently
- **The code diverges from the business language** over time

Domain-Driven Design offers a better way through **rich domain models** built with Entities and Value Objects that embody both data and behavior.

## Philosophical Foundation: Values vs. Identities

Before diving into implementation, we need to understand a fundamental distinction that exists both in the real world and in our domain models:

### The Value vs. Identity Distinction

**Consider a $20 bill:**
- If you have two $20 bills with the same serial number, they represent the same physical bill (identity-based)
- If you have two $20 bills with different serial numbers, they have the same value for purchasing (value-based)
- You don't care which specific $20 bill you use to buy coffee (value semantics)
- But the bank cares about tracking specific bills for fraud prevention (identity semantics)

**In our social media domain:**
- **Email addresses are values**: "alice@example.com" is the same regardless of which Account object contains it
- **Accounts are entities**: Account #12345 is distinct from Account #67890 even if they have the same email temporarily
- **Usernames are values**: The string "alice_smith" has the same meaning everywhere
- **Follow relationships might be entities**: A specific follow relationship has identity and lifecycle

This philosophical distinction drives our technical implementation decisions.

## Value Objects: Representing Concepts, Not Just Data

**Value Objects are more than validated strings.** They represent complete business concepts with:
- **Clear semantics**: What does this value mean in the business context?
- **Invariants**: What rules must always be true?
- **Behavior**: What operations make sense for this concept?
- **Expressiveness**: How does this improve code readability?

### Deep Dive: Email Value Object

Let's build a comprehensive Email value object that goes beyond simple validation:

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Email:
    """
    Represents a validated email address.
    
    Invariants:
    - Must follow RFC-compliant email format
    - Domain must be provided (no local-only emails)
    - Cannot be empty or whitespace
    
    Business Rules:
    - Case-insensitive comparison (alice@EXAMPLE.com == alice@example.com)
    - Normalized storage (always lowercase)
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Email cannot be empty")
        
        normalized = self.value.strip().lower()
        
        # Use more comprehensive email validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", normalized):
            raise ValueError(f"Invalid email format: {self.value}")
        
        # Replace the value with normalized version
        object.__setattr__(self, 'value', normalized)

    @property
    def local_part(self) -> str:
        """Extract the part before @"""
        return self.value.split('@')[0]
    
    @property
    def domain(self) -> str:
        """Extract the domain part"""
        return self.value.split('@')[1]
    
    def is_from_domain(self, domain: str) -> bool:
        """Check if email is from a specific domain"""
        return self.domain.lower() == domain.lower()
    
    def __str__(self) -> str:
        return self.value

# Usage examples showing expressiveness
email = Email("Alice.Smith@EXAMPLE.COM")
print(email.value)              # "alice.smith@example.com" (normalized)
print(email.local_part)         # "alice.smith"
print(email.domain)            # "example.com"
print(email.is_from_domain("example.com"))  # True

# Business rules are enforced
try:
    invalid_email = Email("not-an-email")
except ValueError as e:
    print(f"Caught expected error: {e}")
```

### Why This Design Matters

**Business Expressiveness:**
```python
# Instead of this unclear code:
if user_email.endswith("@company.com"):
    grant_employee_access()

# We can write this expressive code:
if user.email.is_from_domain("company.com"):
    grant_employee_access()
```

**Guaranteed Validity:**
```python
# This is impossible - Email constructor ensures validity
def send_email(to: Email, subject: str, body: str):
    # No need to validate 'to' - it's guaranteed to be valid
    email_service.send(to.value, subject, body)
```

### AccountId: Identity Value Objects

Some Value Objects represent identities themselves. They have value semantics but contain identity information:

```python
import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountId:
    """
    Represents a unique account identifier.
    
    Design decisions:
    - Uses UUID for uniqueness across distributed systems
    - Immutable to prevent accidental modification
    - Contains factory method for new ID generation
    - String representation for easy serialization
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("AccountId cannot be empty")
        
        # Validate UUID format if needed
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid UUID format for AccountId: {self.value}")

    @staticmethod
    def new() -> "AccountId":
        """Generate a new unique AccountId"""
        return AccountId(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, id_string: str) -> "AccountId":
        """Create AccountId from string with validation"""
        return cls(id_string)

    def __str__(self) -> str:
        return self.value
    
    def short_form(self) -> str:
        """Return shortened version for display"""
        return self.value[:8]

# Usage
account_id = AccountId.new()
print(f"New account: {account_id.short_form()}")

# Comparison works by value
id1 = AccountId("550e8400-e29b-41d4-a716-446655440000")
id2 = AccountId("550e8400-e29b-41d4-a716-446655440000")
assert id1 == id2  # True - same value means same identity
```

### Username: Business Rules in Value Objects

Usernames have complex business rules that belong in the Value Object:

```python
import re
from dataclasses import dataclass
from typing import Set

@dataclass(frozen=True)
class Username:
    """
    Represents a valid username for the platform.
    
    Business Rules:
    - 3-32 characters in length
    - Can contain letters, numbers, underscores
    - Cannot start or end with underscore
    - Cannot contain consecutive underscores
    - Case-insensitive for uniqueness checking
    - Reserved words are forbidden
    """
    value: str

    # Reserved usernames that cannot be used
    RESERVED_NAMES: Set[str] = {
        'admin', 'root', 'administrator', 'moderator', 'support',
        'help', 'api', 'www', 'mail', 'email', 'system', 'null',
        'undefined', 'test', 'guest', 'anonymous'
    }

    def __post_init__(self) -> None:
        self._validate_format()
        self._validate_business_rules()

    def _validate_format(self) -> None:
        if not self.value:
            raise ValueError("Username cannot be empty")
        
        if len(self.value) < 3 or len(self.value) > 32:
            raise ValueError("Username must be 3-32 characters long")
        
        if not re.match(r"^[a-zA-Z0-9_]+$", self.value):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        if self.value.startswith('_') or self.value.endswith('_'):
            raise ValueError("Username cannot start or end with underscore")
        
        if '__' in self.value:
            raise ValueError("Username cannot contain consecutive underscores")

    def _validate_business_rules(self) -> None:
        if self.value.lower() in self.RESERVED_NAMES:
            raise ValueError(f"Username '{self.value}' is reserved and cannot be used")

    def normalized(self) -> str:
        """Return normalized form for uniqueness checking"""
        return self.value.lower()
    
    def display_form(self) -> str:
        """Return form suitable for display"""
        return self.value
    
    def __str__(self) -> str:
        return self.value

# Usage
username = Username("Alice_Smith_123")
print(f"Display: {username.display_form()}")
print(f"Normalized: {username.normalized()}")

# Business rules enforced
try:
    reserved_username = Username("admin")
except ValueError as e:
    print(f"Prevented reserved username: {e}")
```

## Entities: Objects with Identity and Lifecycle

**Entities represent concepts that have an identity that persists over time.** Unlike Value Objects, two Entities with the same data might still be different objects if they have different identities.

### The Account Entity

Our Account entity embodies the core concepts from the Account bounded context:

```python
from dataclasses import dataclass, field
from typing import Set, List
from datetime import datetime

@dataclass
class Account:
    """
    Represents a user account in the system.
    
    Invariants:
    - Must have a unique, immutable ID
    - Email must be valid and unique across the system
    - Username must be valid and unique across the system
    - Blocked set cannot contain the account's own ID
    
    Lifecycle:
    - Created via registration
    - Can be activated/deactivated
    - Can accumulate blocked relationships
    - Cannot change core identity information (email, username)
    """
    id: AccountId
    email: Email
    username: Username
    created_at: datetime = field(default_factory=datetime.now)
    blocked_accounts: Set[AccountId] = field(default_factory=set)
    is_active: bool = True

    def __post_init__(self) -> None:
        # Ensure account cannot block itself
        if self.id in self.blocked_accounts:
            raise ValueError("Account cannot block itself")

    def block_account(self, account_id: AccountId) -> 'AccountBlocked':
        """
        Block another account.
        
        Business Rules:
        - Cannot block yourself
        - Blocking is idempotent (no error if already blocked)
        - Returns event describing what happened
        """
        if account_id == self.id:
            raise ValueError("Cannot block yourself")
        
        was_already_blocked = account_id in self.blocked_accounts
        self.blocked_accounts.add(account_id)
        
        return AccountBlocked(
            blocker_id=self.id,
            blocked_id=account_id,
            blocked_at=datetime.now(),
            was_already_blocked=was_already_blocked
        )

    def unblock_account(self, account_id: AccountId) -> 'AccountUnblocked':
        """
        Unblock a previously blocked account.
        
        Business Rules:
        - Unblocking is idempotent (no error if not blocked)
        - Returns event describing what happened
        """
        was_blocked = account_id in self.blocked_accounts
        self.blocked_accounts.discard(account_id)
        
        return AccountUnblocked(
            unblocker_id=self.id,
            unblocked_id=account_id,
            unblocked_at=datetime.now(),
            was_previously_blocked=was_blocked
        )

    def is_blocked(self, account_id: AccountId) -> bool:
        """Check if a specific account is blocked"""
        return account_id in self.blocked_accounts

    def deactivate(self) -> 'AccountDeactivated':
        """
        Deactivate the account.
        
        Business Rules:
        - Can only deactivate active accounts
        - Deactivation should trigger cleanup of relationships
        """
        if not self.is_active:
            raise ValueError("Account is already deactivated")
        
        self.is_active = False
        return AccountDeactivated(
            account_id=self.id,
            deactivated_at=datetime.now()
        )

    def __eq__(self, other) -> bool:
        """Entities are equal if they have the same ID"""
        if not isinstance(other, Account):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets and dictionaries"""
        return hash(self.id)

    def __str__(self) -> str:
        return f"Account({self.username.value})"
```

### Domain Events: Capturing What Happened

Events are the natural output of entity behavior. They should be immutable Value Objects that capture exactly what happened:

```python
from dataclasses import dataclass
from datetime import datetime
from abc import ABC

class DomainEvent(ABC):
    """Base class for all domain events"""
    pass

@dataclass(frozen=True)
class AccountRegistered(DomainEvent):
    """Published when a new account is successfully created"""
    account_id: AccountId
    email: Email
    username: Username
    registered_at: datetime

@dataclass(frozen=True)
class AccountBlocked(DomainEvent):
    """Published when one account blocks another"""
    blocker_id: AccountId
    blocked_id: AccountId
    blocked_at: datetime
    was_already_blocked: bool

@dataclass(frozen=True)
class AccountUnblocked(DomainEvent):
    """Published when one account unblocks another"""
    unblocker_id: AccountId
    unblocked_id: AccountId
    unblocked_at: datetime
    was_previously_blocked: bool

@dataclass(frozen=True)
class AccountDeactivated(DomainEvent):
    """Published when an account is deactivated"""
    account_id: AccountId
    deactivated_at: datetime
```

## Entity vs Value Object: Decision Framework

**When to use Value Objects:**
- ✅ **Describes something**: Email, Money, Address, Color
- ✅ **Equality by value**: Two emails with same text are the same
- ✅ **No identity needed**: Don't need to track which specific email object
- ✅ **Immutable by nature**: Changing email creates new email
- ✅ **Used as property**: Entities contain value objects

**When to use Entities:**
- ✅ **Represents something**: Account, Order, Product, Person
- ✅ **Has lifecycle**: Created, modified, deleted over time
- ✅ **Identity matters**: Account #123 ≠ Account #456 even with same data
- ✅ **Mutable state**: Properties can change while maintaining identity
- ✅ **Has behavior**: Methods that implement business rules

### Examples from Our Domain

| Concept | Type | Reasoning |
|---------|------|-----------|
| `Email` | Value Object | Same email text = same email, immutable |
| `Username` | Value Object | Same username text = same username, immutable |
| `AccountId` | Value Object | Identity value, immutable, equality by value |
| `Account` | Entity | Has lifecycle, identity persists through changes |
| `FollowRelationship` | Entity | Has identity, can be created/removed over time |
| `BlockedDate` | Value Object | Just a timestamp, immutable |

## Common Anti-Patterns and How to Avoid Them

### Anti-Pattern 1: Anemic Value Objects

❌ **Wrong approach:**
```python
@dataclass
class Email:
    value: str  # Just a string wrapper
```

✅ **Better approach:**
```python
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        # Validation logic
        
    def domain(self) -> str:
        # Business behavior
        
    def is_corporate(self) -> bool:
        # Domain-specific queries
```

### Anti-Pattern 2: Entities as Data Containers

❌ **Wrong approach:**
```python
@dataclass
class Account:
    id: str
    email: str
    username: str
    blocked_users: List[str]
    
    # No behavior, just getters/setters elsewhere
```

✅ **Better approach:**
```python
@dataclass
class Account:
    id: AccountId
    email: Email  
    username: Username
    blocked_accounts: Set[AccountId]
    
    def block_account(self, account_id: AccountId) -> AccountBlocked:
        # Business logic here
```

### Anti-Pattern 3: Primitive Obsession

❌ **Wrong approach:**
```python
def register_user(email: str, username: str) -> str:
    if "@" not in email:  # Validation scattered everywhere
        raise ValueError("Invalid email")
    # ... more validation and logic
```

✅ **Better approach:**
```python
def register_user(email: Email, username: Username) -> AccountId:
    # Validation handled by Value Objects
    # Business logic is clear and focused
```

### Anti-Pattern 4: Mutable Value Objects

❌ **Wrong approach:**
```python
@dataclass
class Email:
    value: str
    
    def set_value(self, new_value: str):  # Violates immutability
        self.value = new_value
```

✅ **Better approach:**
```python
@dataclass(frozen=True)
class Email:
    value: str
    
    def with_different_domain(self, new_domain: str) -> 'Email':
        local_part = self.value.split('@')[0]
        return Email(f"{local_part}@{new_domain}")
```

## Advanced Patterns: Result Types for Robust Error Handling

Instead of exceptions for business rule violations, consider Result types:

```python
from dataclasses import dataclass
from typing import Union, Generic, TypeVar
from abc import ABC

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Success(Generic[T]):
    value: T

@dataclass(frozen=True)
class Failure(Generic[E]):
    error: E

Result = Union[Success[T], Failure[E]]

# Usage in Value Objects
@dataclass(frozen=True)
class EmailValidationError:
    message: str
    invalid_value: str

@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def create(cls, value: str) -> Result[Email, EmailValidationError]:
        """Factory method that returns Result instead of raising exceptions"""
        if not value or not value.strip():
            return Failure(EmailValidationError("Email cannot be empty", value))
        
        normalized = value.strip().lower()
        
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", normalized):
            return Failure(EmailValidationError("Invalid email format", value))
        
        return Success(cls(normalized))

# Usage
email_result = Email.create("user@example.com")
if isinstance(email_result, Success):
    email = email_result.value
    print(f"Valid email: {email}")
else:
    error = email_result.error
    print(f"Invalid email: {error.message}")
```

## Testing Entities and Value Objects

### Testing Value Objects

```python
import pytest

def test_email_validation():
    # Test valid emails
    valid_email = Email("user@example.com")
    assert valid_email.value == "user@example.com"
    assert valid_email.domain == "example.com"
    
    # Test normalization
    normalized_email = Email("USER@EXAMPLE.COM")
    assert normalized_email.value == "user@example.com"
    
    # Test invalid emails
    with pytest.raises(ValueError):
        Email("invalid-email")
    
    with pytest.raises(ValueError):
        Email("")

def test_email_equality():
    email1 = Email("user@example.com")
    email2 = Email("USER@EXAMPLE.COM")  # Different case
    assert email1 == email2  # Should be equal after normalization

def test_email_immutability():
    email = Email("user@example.com")
    # This should be impossible due to frozen=True
    with pytest.raises(AttributeError):
        email.value = "different@example.com"
```

### Testing Entities

```python
def test_account_blocking():
    alice_id = AccountId.new()
    bob_id = AccountId.new()
    
    alice = Account(
        id=alice_id,
        email=Email("alice@example.com"),
        username=Username("alice")
    )
    
    # Test blocking
    event = alice.block_account(bob_id)
    
    assert isinstance(event, AccountBlocked)
    assert event.blocker_id == alice_id
    assert event.blocked_id == bob_id
    assert not event.was_already_blocked
    assert alice.is_blocked(bob_id)

def test_account_cannot_block_self():
    alice_id = AccountId.new()
    alice = Account(
        id=alice_id,
        email=Email("alice@example.com"),
        username=Username("alice")
    )
    
    with pytest.raises(ValueError, match="Cannot block yourself"):
        alice.block_account(alice_id)

def test_account_equality():
    alice_id = AccountId.new()
    
    alice1 = Account(
        id=alice_id,
        email=Email("alice@example.com"),
        username=Username("alice")
    )
    
    alice2 = Account(
        id=alice_id,
        email=Email("different@example.com"),  # Different data
        username=Username("different")
    )
    
    # Same ID = same entity, regardless of other data
    assert alice1 == alice2
```

## Real-World Considerations

### Performance Implications

**Value Object Creation:**
- Value objects are created frequently, so constructor performance matters
- Consider caching for commonly used values
- Be mindful of validation complexity

**Entity Lifecycle:**
- Entities live longer, so memory usage matters
- Consider lazy loading for expensive properties
- Design for efficient serialization

### Serialization and Persistence

```python
@dataclass(frozen=True)
class Email:
    value: str
    
    def to_dict(self) -> dict:
        """Serialize for JSON/database storage"""
        return {"value": self.value}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Email':
        """Deserialize from JSON/database"""
        return cls(data["value"])

@dataclass
class Account:
    id: AccountId
    email: Email
    username: Username
    
    def to_dict(self) -> dict:
        """Serialize entity state"""
        return {
            "id": self.id.value,
            "email": self.email.to_dict(),
            "username": self.username.value,
            "blocked_accounts": [id.value for id in self.blocked_accounts]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """Reconstitute entity from stored state"""
        return cls(
            id=AccountId(data["id"]),
            email=Email.from_dict(data["email"]),
            username=Username(data["username"]),
            blocked_accounts={AccountId(id) for id in data.get("blocked_accounts", [])}
        )
```

## Summary: Building Rich Domain Models

Entities and Value Objects are the building blocks of expressive domain models that:

🎯 **Encapsulate business rules** in the right places
🎯 **Make invalid states unrepresentable** through careful design
🎯 **Express business concepts clearly** in code
🎯 **Maintain consistency** through invariants
🎯 **Enable confident refactoring** through strong typing

**Key Design Principles:**
- **Value Objects** represent descriptions and measurements
- **Entities** represent things with identity and lifecycle
- **Both should be rich with behavior**, not just data containers
- **Validation belongs in constructors**, making invalid states impossible
- **Business rules belong in domain objects**, not scattered in services

In our social media platform, we've built:
- **Rich Value Objects** for Email, Username, and AccountId that enforce business rules
- **Behavioral Entities** like Account that implement domain logic
- **Immutable Events** that capture what happened in a business-meaningful way

This foundation provides the building blocks for implementing the policies and workflows we discovered in Part 1, while ensuring our code remains expressive and maintainable.

---

**Next:** [Part 3 - Repositories and Aggregates](/courses/03-repositories-aggregates/) - Learn how to design persistence that serves the domain, not the database.
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

# Entities and Value Objects

**Goal:** Represent the ubiquitous language in code. Use events to derive attributes.

## Core Heuristics

### Value Object
- **Identity by value** - two Value Objects with same data are equal
- **Immutable** - cannot be changed after creation
- **Validated at creation** - invalid data cannot exist
- **Examples:** Email, Username, AccountId

### Entity  
- **Identity by id** - equality determined by unique identifier
- **Has lifecycle** - can change state over time
- **Contains behaviour** - methods that implement business rules
- **Example:** Account

### Aggregate
- **Consistency boundary** - maintains business invariants
- **Choose small, stable boundaries** - easier to maintain and scale
- **Today's approach:** Keep Account and Follow as separate aggregates

## Design Checklist

⭐ **Every Entity has a stable id**
⭐ **Every Value Object validates on creation**  
⭐ **Derive attributes from events:** AccountRegistered reveals email and username

## Code Examples

### Value Objects

```python
@dataclass(frozen=True)
class AccountId:
    value: str

    @staticmethod
    def new() -> "AccountId":
        return AccountId(str(uuid.uuid4()))

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.value):
            raise ValueError("Invalid email")

@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[a-zA-Z0-9_]{3,32}$", self.value):
            raise ValueError("Invalid username")
```

### Entity

```python
@dataclass
class Account:
    id: AccountId
    email: Email
    username: Username
    blocked: set[AccountId] = field(default_factory=set)

    def block(self, other: AccountId) -> AccountBlocked:
        if other in self.blocked:
            # idempotent
            return AccountBlocked(self.id, other)
        self.blocked.add(other)
        return AccountBlocked(self.id, other)
```

## Domain Events

Events capture what happened in the past tense:

```python
@dataclass(frozen=True)
class AccountRegistered(Event):
    account_id: AccountId
    email: Email
    username: Username

@dataclass(frozen=True)
class AccountBlocked(Event):
    blocker_id: AccountId
    blocked_id: AccountId
```

## Exercises

### Extend the Model
* Extend Account with a profile `display_name` as a Value Object.
* Decide where the rule "username cannot change" lives: entity method vs application policy.

### Three-Step Improvement

**Immediate patch:** Freeze Value Objects with `@dataclass(frozen=True)`.

**Deeper cause:** Conflating Value Object equality with Entity identity.

**Optional improvement:** Add factory methods that return Result types instead of exceptions to capture validation failures as domain data.

---

**Next:** [Part 3 - Repositories and Aggregates](/courses/03-repositories-aggregates/) - Learn how persistence is a secondary concern and design repository interfaces around domain needs.
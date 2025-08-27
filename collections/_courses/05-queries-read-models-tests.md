---
layout: course
title: "DDD Workshop Part 5: Queries, Read Models, Tests"
part: "Part 5 of 5"
duration: "90 minutes"
prev_course: "/courses/04-commands-handlers-events-policies/"
prev_title: "Commands, Handlers, Events, Policies"
order: 5
---

# Queries, Read Models, Tests

**Goal:** Keep reads simple. Project events into read models fit for purpose.

## Read Models: Separate from Write Models

❌ **Don't do this:** Query your aggregate directly  
✅ **Do this:** Build separate read models optimized for queries

### Why Separate Read Models?

- **Different optimization needs** - writes need consistency, reads need speed
- **Different data shapes** - UI needs different views than business logic
- **Easier to scale** - can be stored in different databases  
- **Simpler queries** - no complex joins needed

## Event Projector

Build a tiny projector that listens to events and maintains read models:

```python
class Application:
    def __init__(self, accounts: AccountRepository, follows: FollowRepository) -> None:
        # ... other initialization ...
        
        # Simple read model
        self.read_followers: DefaultDict[str, set[str]] = defaultdict(set)
        self.read_following: DefaultDict[str, set[str]] = defaultdict(set)
        
        # Subscribe to events
        self.bus.subscribe(AccountRegistered, self._project)
        self.bus.subscribe(AccountFollowed, self._project)
        self.bus.subscribe(FollowerRemoved, self._project)

    def _project(self, ev: Event) -> None:
        if isinstance(ev, AccountRegistered):
            # Nothing to project for follows
            return
        if isinstance(ev, AccountFollowed):
            self.read_following[ev.follower_id.value].add(ev.followee_id.value)
            self.read_followers[ev.followee_id.value].add(ev.follower_id.value)
        if isinstance(ev, FollowerRemoved):
            self.read_following[ev.follower_id.value].discard(ev.followee_id.value)
            self.read_followers[ev.followee_id.value].discard(ev.follower_id.value)
```

## Complete Working Example

Here's the full working code that demonstrates all concepts:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Dict, List, Callable, Type, DefaultDict, Optional
from collections import defaultdict
import re
import uuid

# Value Objects
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

# Events and Commands (abbreviated for space)
# ... [see full code in workshop] ...

# The demo that proves the bug is fixed:
def demo() -> None:
    accounts = InMemoryAccountRepo()
    follows = InMemoryFollowRepo()
    app = Application(accounts, follows)

    # Register two users
    [ev1] = app.handle(RegisterAccount(Email("a@example.com"), Username("alice_uk")))
    [ev2] = app.handle(RegisterAccount(Email("b@example.com"), Username("bob_uk")))
    a = ev1.account_id
    b = ev2.account_id

    # Alice follows Bob
    app.handle(FollowAccount(follower_id=a, followee_id=b))
    print("Before block: A follows ->", sorted(app.read_following[a.value]))

    # Bob blocks Alice
    app.handle(BlockAccount(blocker_id=b, blocked_id=a))

    # Policy should have removed the follow
    print("After block:  A follows ->", sorted(app.read_following[a.value]))
```

**Expected output:**
```
Before block: A follows -> ['<bob-id>']
After block:  A follows -> []
```

This proves our policy fixed the bug! 🎉

## Scenario Test

Write a test that captures the entire scenario:

```python
def test_block_removes_follow_relationship():
    # Arrange
    accounts = InMemoryAccountRepo()
    follows = InMemoryFollowRepo()
    app = Application(accounts, follows)
    
    # Register users
    [alice_reg] = app.handle(RegisterAccount(Email("alice@test.com"), Username("alice")))
    [bob_reg] = app.handle(RegisterAccount(Email("bob@test.com"), Username("bob")))
    alice_id = alice_reg.account_id
    bob_id = bob_reg.account_id
    
    # Alice follows Bob
    app.handle(FollowAccount(follower_id=alice_id, followee_id=bob_id))
    assert bob_id.value in app.read_following[alice_id.value]
    
    # Act: Bob blocks Alice
    app.handle(BlockAccount(blocker_id=bob_id, blocked_id=alice_id))
    
    # Assert: Alice no longer follows Bob
    assert bob_id.value not in app.read_following[alice_id.value]
```

## Exercises

### Build Query Functions
* Write a function `get_relationship(a, b)` returning `{"a_follows_b": bool, "b_follows_a": bool, "a_blocked_by_b": bool, "b_blocked_by_a": bool}` based on the read model.
* Add a scenario test for the self-follow rejection.

### Three-Step Improvement

**Immediate patch:** Project only what your UI needs.

**Deeper cause:** Trying to query write models directly.

**Optional improvement:** Persist the read model separately and rebuild it from an event stream during start-up.

## Key Testing Insights

🎯 **Scenario tests are gold** - test the full user journey  
🎯 **Test business rules** - not technical implementation details
🎯 **Start with happy path** - then add edge cases
🎯 **Use real examples** - from your event storming session

## Where To Take It Next

### Production-Ready Features
* **Add a UnitOfWork** and transactional boundaries
* **Add real persistence** - wrap your repository Protocols with PostgreSQL or SQLite 
* **Introduce event streams** - rebuild read models from events
* **Integrate with workflow engines** - command handlers become activities

### Context Mapping  
* **Add context mapping** between Accounts and SocialGraph
* **Define upstream and downstream** relationships
* **Protect with anti-corruption layer** at boundaries

### Reference Architecture
```
src/
  app/
    application.py          # registers handlers and policies
    policies.py             # event -> command mappings
    handlers.py             # 4 step handlers
  domain/
    value_objects.py
    entities.py
    events.py
    commands.py
    repositories.py         # Protocols only
  infra/
    event_bus.py
    repo_inmemory.py
tests/
  test_follow_block_policy.py
```

**Start single file. Split only once the team understands the flow.**

## Workshop Completed! 🎉

You now have:
✅ **Domain discovery** with event storming  
✅ **Clean domain model** with entities and value objects
✅ **Testable architecture** with repositories and aggregates  
✅ **Business rule enforcement** with commands, handlers, and policies
✅ **Optimized queries** with read models
✅ **Bug-free social app** that properly handles blocking

**Congratulations on completing the DDD Workshop!**

---

**Want to continue learning?** Check out more advanced DDD patterns and explore how to apply these concepts to your own domain challenges.
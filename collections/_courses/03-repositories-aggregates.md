---
layout: course
title: "DDD Workshop Part 3: Repositories and Aggregates"
part: "Part 3 of 5"
duration: "90 minutes"
prev_course: "/courses/02-entities-value-objects/"
prev_title: "Entities and Value Objects"
next_course: "/courses/04-commands-handlers-events-policies/"
next_title: "Commands, Handlers, Events, Policies"
order: 3
---

# Repositories and Aggregates

**Goal:** Persistence is a secondary concern. Design repository interfaces around domain needs, not tables.

## Repository Design Principles

🎯 **Domain-first interfaces** - start with what the domain needs, not database structure
🎯 **Hide data structures** behind clean Protocol interfaces  
🎯 **Think in aggregates** - not database rows

## Repository Interface Examples

### AccountRepository
```python
class AccountRepository(Protocol):
    def get(self, account_id: AccountId) -> Optional[Account]: ...
    def get_by_email(self, email: Email) -> Optional[Account]: ...
    def get_by_username(self, username: Username) -> Optional[Account]: ...
    def save(self, account: Account) -> None: ...
```

### FollowRepository  
```python
class FollowRepository(Protocol):
    def exists(self, follower: AccountId, followee: AccountId) -> bool: ...
    def add(self, follower: AccountId, followee: AccountId) -> None: ...
    def remove(self, follower: AccountId, followee: AccountId) -> None: ...
    def followers_of(self, account: AccountId) -> List[AccountId]: ...
    def following_of(self, account: AccountId) -> List[AccountId]: ...
```

## In-Memory Implementation

Perfect for workshops and testing:

```python
class InMemoryAccountRepo(AccountRepository):
    def __init__(self) -> None:
        self.by_id: Dict[str, Account] = {}
        self.by_email: Dict[str, str] = {}
        self.by_username: Dict[str, str] = {}

    def get(self, account_id: AccountId) -> Optional[Account]:
        return self.by_id.get(account_id.value)

    def get_by_email(self, email: Email) -> Optional[Account]:
        aid = self.by_email.get(email.value)
        return self.by_id.get(aid) if aid else None

    def save(self, account: Account) -> None:
        self.by_id[account.id.value] = account
        self.by_email[account.email.value] = account.id.value
        self.by_username[account.username.value] = account.id.value
```

```python
class InMemoryFollowRepo(FollowRepository):
    def __init__(self) -> None:
        self.following: Dict[str, set[str]] = defaultdict(set)   # follower -> set(followee)
        self.followers: Dict[str, set[str]] = defaultdict(set)   # followee -> set(follower)

    def exists(self, follower: AccountId, followee: AccountId) -> bool:
        return followee.value in self.following[follower.value]

    def add(self, follower: AccountId, followee: AccountId) -> None:
        if self.exists(follower, followee):
            return
        self.following[follower.value].add(followee.value)
        self.followers[followee.value].add(follower.value)
```

## Aggregate Rules for Today

✅ **An Account can block many others**
✅ **A Follow is a relation between two Account ids**  
✅ **You cannot follow someone who has blocked you or whom you have blocked**

## Why Separate Aggregates?

We keep **Account** and **Follow** as separate aggregates because:

- **Different consistency boundaries** - blocking and following have different rules
- **Different scalability needs** - follows might be high-volume
- **Simpler to reason about** - smaller bounded contexts

## Exercises

### Repository Optimization
* Make `FollowRepository.exists()` constant time using a composite key set.
* Add a repository method you actually need: `followers_of(account_id)` is fine. Do not mirror database rows.

### Three-Step Improvement

**Immediate patch:** Hide data structures behind Protocols.

**Deeper cause:** Letting storage shape the model.

**Optional improvement:** Introduce a Unit of Work interface with commit and rollback. Keep it in memory for now.

## Key Takeaways

1. **Repository interfaces come from domain needs** - not database schema
2. **Protocols enable easy testing** - swap implementations freely  
3. **In-memory implementations are perfect** for workshops and fast tests
4. **Start simple** - add complexity only when needed

---

**Next:** [Part 4 - Commands, Handlers, Events, Policies](/courses/04-commands-handlers-events-policies/) - Learn the 4-step command handling pattern and implement business policies.
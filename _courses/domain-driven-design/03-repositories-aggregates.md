---
course: DDD 101
part: 3
title: "DDD 101 - Part 3: Repositories and Aggregates"
---

# Repositories and Aggregates: Domain-Driven Persistence

**Goal:** Design persistence that serves the domain, not the database. Create aggregate boundaries that maintain business invariants and enable repository patterns that express business needs.

## Introduction: The Persistence Trap

Most applications fall into the **persistence-driven design trap**. They start with database schema design, then build objects that mirror tables, and end up with repositories that are thin wrappers around CRUD operations. This approach fails because:

- **Domain logic spreads into services** instead of staying in domain objects
- **Database structure drives domain model** instead of business rules
- **Consistency boundaries are unclear** leading to data corruption
- **Business operations require multiple repository calls** creating transaction complexity

Domain-Driven Design flips this relationship: **the domain defines persistence needs, not the other way around.**

## The Repository Pattern: Collection Metaphor

Think of repositories as **in-memory collections of domain objects**. This metaphor is powerful because:

- **Collections are simple**: You put objects in, you get objects out
- **Collections hide implementation**: You don't care if it's an array, hash table, or tree
- **Collections support queries**: Find objects by their properties
- **Collections maintain object identity**: The same object comes out that went in

```python
# Think of repositories like this conceptual interface
class Collection[T]:
    def add(self, item: T) -> None: ...
    def remove(self, item: T) -> None: ...
    def find(self, predicate: Callable[[T], bool]) -> Optional[T]: ...
    def filter(self, predicate: Callable[[T], bool]) -> List[T]: ...
```

This abstraction lets domain logic work with objects without worrying about SQL, NoSQL, files, or any other persistence mechanism.

## Aggregate Design: Consistency Boundaries

**Aggregates are clusters of domain objects that are treated as a single unit for data changes.** They define:

- **Consistency boundaries**: What invariants must be maintained together
- **Transaction boundaries**: What changes succeed or fail together  
- **Concurrency boundaries**: What gets locked together
- **Persistence boundaries**: What gets saved together

### Aggregate Design Principles

**1. Small Aggregates Are Better**
Large aggregates create:
- Performance bottlenecks (larger transactions)
- Concurrency conflicts (more lock contention)
- Complexity in maintaining invariants

**2. Reference Other Aggregates by ID Only**
Aggregates should not hold direct references to other aggregates:
```python
# ❌ Don't do this
@dataclass
class Account:
    followers: List[Account]  # Direct references

# ✅ Do this instead  
@dataclass
class Account:
    id: AccountId
    # Followers managed separately
    
class FollowService:
    def get_followers(self, account_id: AccountId) -> List[AccountId]: ...
```

**3. One Repository Per Aggregate**
Each aggregate root gets exactly one repository. This enforces the aggregate boundary and ensures consistent access patterns.

**4. Aggregate Roots Are Entry Points**
All access to objects within an aggregate must go through the aggregate root. This allows the root to maintain invariants.

### Designing Our Aggregates

Let's analyze our social media domain and design appropriate aggregates:

#### Option 1: Single Large Aggregate ❌

```python
@dataclass
class SocialAccount:  # Too large!
    id: AccountId
    email: Email
    username: Username
    profile: Profile
    followers: Set[AccountId]
    following: Set[AccountId]
    blocked_accounts: Set[AccountId]
    posts: List[Post]
    # ... lots more
```

**Problems:**
- Huge transaction boundaries
- High contention (following someone locks their entire social graph)
- Complex invariants to maintain
- Performance issues

#### Option 2: Separate Aggregates ✅

```python
# Account Aggregate - Identity and Core Profile
@dataclass
class Account:
    id: AccountId
    email: Email
    username: Username
    blocked_accounts: Set[AccountId]
    is_active: bool

# Follow Aggregate - Relationship Management  
@dataclass
class FollowRelationship:
    id: FollowRelationshipId
    follower_id: AccountId
    followee_id: AccountId
    created_at: datetime
    is_active: bool
```

**Benefits:**
- Smaller transaction boundaries
- Lower contention
- Clear responsibilities
- Independent scalability

## Repository Interface Design

Design repository interfaces from the **domain's perspective**, not the database perspective:

### AccountRepository: Domain-Focused Interface

```python
from typing import Protocol, Optional, List
from abc import abstractmethod

class AccountRepository(Protocol):
    """
    Repository for Account aggregate.
    
    Design principles:
    - Methods reflect business operations, not database operations
    - Return domain objects, not data structures
    - Hide persistence implementation details
    - Support business queries, not just CRUD
    """
    
    @abstractmethod
    def save(self, account: Account) -> None:
        """
        Save an account to persistent storage.
        
        Business rules:
        - Idempotent operation (safe to call multiple times)
        - Handles both new accounts and updates
        - Enforces uniqueness constraints (email, username)
        """
        pass
    
    @abstractmethod
    def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        """Get account by its unique identifier"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[Account]:
        """
        Find account by email address.
        
        Business context: Used for login and duplicate checking
        """
        pass
    
    @abstractmethod
    def get_by_username(self, username: Username) -> Optional[Account]:
        """
        Find account by username.
        
        Business context: Used for mentions, profile lookup, duplicate checking
        """
        pass
    
    @abstractmethod
    def find_active_accounts(self, account_ids: List[AccountId]) -> List[Account]:
        """
        Get multiple active accounts by their IDs.
        
        Business context: Used for validating follow/block operations
        """
        pass
    
    @abstractmethod
    def exists_with_email(self, email: Email) -> bool:
        """
        Check if an account exists with the given email.
        
        Business context: Fast duplicate checking during registration
        """
        pass
    
    @abstractmethod
    def exists_with_username(self, username: Username) -> bool:
        """
        Check if an account exists with the given username.
        
        Business context: Fast duplicate checking during registration
        """
        pass
```

### FollowRepository: Relationship-Focused Interface

```python
class FollowRepository(Protocol):
    """
    Repository for Follow relationships.
    
    Design focus: Express relationship queries naturally
    """
    
    @abstractmethod
    def save_relationship(self, relationship: FollowRelationship) -> None:
        """Save a follow relationship"""
        pass
    
    @abstractmethod
    def remove_relationship(self, follower_id: AccountId, followee_id: AccountId) -> bool:
        """
        Remove a follow relationship.
        
        Returns: True if relationship existed and was removed, False if didn't exist
        """
        pass
    
    @abstractmethod
    def exists(self, follower_id: AccountId, followee_id: AccountId) -> bool:
        """Check if a follow relationship exists"""
        pass
    
    @abstractmethod
    def get_followers(self, account_id: AccountId) -> List[AccountId]:
        """Get all accounts following the given account"""
        pass
    
    @abstractmethod
    def get_following(self, account_id: AccountId) -> List[AccountId]:
        """Get all accounts the given account is following"""
        pass
    
    @abstractmethod
    def get_mutual_follows(self, account_id: AccountId) -> List[AccountId]:
        """
        Get accounts that both follow and are followed by the given account.
        
        Business context: Finding close connections, mutual friends
        """
        pass
    
    @abstractmethod
    def count_followers(self, account_id: AccountId) -> int:
        """Get follower count for display purposes"""
        pass
    
    @abstractmethod
    def count_following(self, account_id: AccountId) -> int:
        """Get following count for display purposes"""
        pass
```

## Implementation: In-Memory Repositories

For development, testing, and workshops, in-memory implementations are perfect:

### InMemoryAccountRepository

```python
from typing import Dict, Optional, List

class InMemoryAccountRepository:
    """
    In-memory implementation of AccountRepository.
    
    Perfect for:
    - Unit testing (fast, isolated)
    - Development (no database setup)
    - Workshops (focus on domain, not infrastructure)
    - Integration testing (predictable state)
    """
    
    def __init__(self) -> None:
        # Multiple indexes for efficient lookup
        self._accounts_by_id: Dict[str, Account] = {}
        self._accounts_by_email: Dict[str, Account] = {}
        self._accounts_by_username: Dict[str, Account] = {}
    
    def save(self, account: Account) -> None:
        """
        Save account with automatic indexing.
        
        Handles uniqueness constraints by checking existing indexes
        """
        # Check for email conflicts (excluding current account)
        existing_email = self._accounts_by_email.get(account.email.value)
        if existing_email and existing_email.id != account.id:
            raise ValueError(f"Email {account.email.value} is already taken")
        
        # Check for username conflicts (excluding current account)
        existing_username = self._accounts_by_username.get(account.username.normalized())
        if existing_username and existing_username.id != account.id:
            raise ValueError(f"Username {account.username.value} is already taken")
        
        # Remove old indexes if this is an update
        old_account = self._accounts_by_id.get(account.id.value)
        if old_account:
            self._remove_from_indexes(old_account)
        
        # Add to all indexes
        self._accounts_by_id[account.id.value] = account
        self._accounts_by_email[account.email.value] = account
        self._accounts_by_username[account.username.normalized()] = account
    
    def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        return self._accounts_by_id.get(account_id.value)
    
    def get_by_email(self, email: Email) -> Optional[Account]:
        return self._accounts_by_email.get(email.value)
    
    def get_by_username(self, username: Username) -> Optional[Account]:
        return self._accounts_by_username.get(username.normalized())
    
    def find_active_accounts(self, account_ids: List[AccountId]) -> List[Account]:
        """Return only active accounts from the given IDs"""
        accounts = []
        for account_id in account_ids:
            account = self.get_by_id(account_id)
            if account and account.is_active:
                accounts.append(account)
        return accounts
    
    def exists_with_email(self, email: Email) -> bool:
        return email.value in self._accounts_by_email
    
    def exists_with_username(self, username: Username) -> bool:
        return username.normalized() in self._accounts_by_username
    
    def _remove_from_indexes(self, account: Account) -> None:
        """Remove account from all indexes"""
        self._accounts_by_email.pop(account.email.value, None)
        self._accounts_by_username.pop(account.username.normalized(), None)
    
    # Testing and debugging utilities
    def clear(self) -> None:
        """Clear all data - useful for tests"""
        self._accounts_by_id.clear()
        self._accounts_by_email.clear()
        self._accounts_by_username.clear()
    
    def count(self) -> int:
        """Get total number of accounts"""
        return len(self._accounts_by_id)
```

### InMemoryFollowRepository

```python
from collections import defaultdict
from typing import DefaultDict, Set, List

class InMemoryFollowRepository:
    """
    In-memory implementation optimized for relationship queries.
    
    Uses bidirectional indexes for O(1) lookups in both directions.
    """
    
    def __init__(self) -> None:
        # Bidirectional relationship tracking
        self._following: DefaultDict[str, Set[str]] = defaultdict(set)  # follower -> {followees}
        self._followers: DefaultDict[str, Set[str]] = defaultdict(set)  # followee -> {followers}
        
        # Relationship objects for full data
        self._relationships: Dict[Tuple[str, str], FollowRelationship] = {}
    
    def save_relationship(self, relationship: FollowRelationship) -> None:
        """Save a follow relationship with bidirectional indexing"""
        follower_id = relationship.follower_id.value
        followee_id = relationship.followee_id.value
        
        # Prevent self-following at repository level
        if follower_id == followee_id:
            raise ValueError("Cannot follow yourself")
        
        # Add to bidirectional indexes
        self._following[follower_id].add(followee_id)
        self._followers[followee_id].add(follower_id)
        
        # Store full relationship
        key = (follower_id, followee_id)
        self._relationships[key] = relationship
    
    def remove_relationship(self, follower_id: AccountId, followee_id: AccountId) -> bool:
        """Remove relationship and return whether it existed"""
        follower_str = follower_id.value
        followee_str = followee_id.value
        
        # Check if relationship exists
        existed = followee_str in self._following[follower_str]
        
        if existed:
            # Remove from bidirectional indexes
            self._following[follower_str].discard(followee_str)
            self._followers[followee_str].discard(follower_str)
            
            # Remove relationship object
            key = (follower_str, followee_str)
            self._relationships.pop(key, None)
        
        return existed
    
    def exists(self, follower_id: AccountId, followee_id: AccountId) -> bool:
        """O(1) existence check"""
        return followee_id.value in self._following[follower_id.value]
    
    def get_followers(self, account_id: AccountId) -> List[AccountId]:
        """Get all followers of an account"""
        follower_ids = self._followers[account_id.value]
        return [AccountId(fid) for fid in follower_ids]
    
    def get_following(self, account_id: AccountId) -> List[AccountId]:
        """Get all accounts this account follows"""
        following_ids = self._following[account_id.value]
        return [AccountId(fid) for fid in following_ids]
    
    def get_mutual_follows(self, account_id: AccountId) -> List[AccountId]:
        """Get accounts that both follow and are followed by the given account"""
        account_str = account_id.value
        following = self._following[account_str]
        followers = self._followers[account_str]
        
        # Intersection of following and followers
        mutual = following & followers
        return [AccountId(mid) for mid in mutual]
    
    def count_followers(self, account_id: AccountId) -> int:
        """O(1) follower count"""
        return len(self._followers[account_id.value])
    
    def count_following(self, account_id: AccountId) -> int:
        """O(1) following count"""
        return len(self._following[account_id.value])
    
    # Bulk operations for complex queries
    def remove_all_relationships_for_account(self, account_id: AccountId) -> int:
        """
        Remove all relationships involving an account.
        
        Business context: Account deletion cleanup
        Returns: Number of relationships removed
        """
        account_str = account_id.value
        removed_count = 0
        
        # Remove all relationships where this account is the follower
        for followee_str in list(self._following[account_str]):
            self.remove_relationship(account_id, AccountId(followee_str))
            removed_count += 1
        
        # Remove all relationships where this account is the followee
        for follower_str in list(self._followers[account_str]):
            self.remove_relationship(AccountId(follower_str), account_id)
            removed_count += 1
        
        return removed_count
    
    def clear(self) -> None:
        """Clear all data - useful for tests"""
        self._following.clear()
        self._followers.clear()
        self._relationships.clear()
```

## Aggregate Lifecycle Management

Aggregates have complex lifecycles that repositories must support:

### Account Aggregate Lifecycle

```python
@dataclass
class Account:
    # ... previous fields ...
    
    @classmethod
    def register(cls, email: Email, username: Username) -> Tuple['Account', 'AccountRegistered']:
        """
        Factory method for creating new accounts.
        
        Returns both the account and the event describing what happened.
        This pattern ensures events are always generated for state changes.
        """
        account_id = AccountId.new()
        account = cls(
            id=account_id,
            email=email,
            username=username,
            created_at=datetime.now(),
            is_active=True
        )
        
        event = AccountRegistered(
            account_id=account_id,
            email=email,
            username=username,
            registered_at=account.created_at
        )
        
        return account, event
    
    def deactivate(self) -> 'AccountDeactivated':
        """
        Deactivate the account.
        
        Business rules:
        - Can only deactivate active accounts
        - Deactivation should trigger relationship cleanup
        """
        if not self.is_active:
            raise ValueError("Account is already deactivated")
        
        self.is_active = False
        
        return AccountDeactivated(
            account_id=self.id,
            deactivated_at=datetime.now(),
            reason="user_requested"
        )
    
    def reactivate(self) -> 'AccountReactivated':
        """Reactivate a deactivated account"""
        if self.is_active:
            raise ValueError("Account is already active")
        
        self.is_active = True
        
        return AccountReactivated(
            account_id=self.id,
            reactivated_at=datetime.now()
        )
```

### FollowRelationship Aggregate

```python
@dataclass
class FollowRelationship:
    """
    Represents a follow relationship between two accounts.
    
    Aggregate responsibilities:
    - Maintain relationship state
    - Enforce relationship business rules
    - Generate appropriate events
    """
    id: FollowRelationshipId
    follower_id: AccountId
    followee_id: AccountId
    created_at: datetime
    is_active: bool = True
    
    @classmethod
    def create(cls, follower_id: AccountId, followee_id: AccountId) -> Tuple['FollowRelationship', 'FollowCreated']:
        """
        Factory method for creating follow relationships.
        
        Business rules enforced at creation:
        - Cannot follow yourself (though this is also checked at service level)
        """
        if follower_id == followee_id:
            raise ValueError("Cannot follow yourself")
        
        relationship_id = FollowRelationshipId.new()
        relationship = cls(
            id=relationship_id,
            follower_id=follower_id,
            followee_id=followee_id,
            created_at=datetime.now()
        )
        
        event = FollowCreated(
            relationship_id=relationship_id,
            follower_id=follower_id,
            followee_id=followee_id,
            created_at=relationship.created_at
        )
        
        return relationship, event
    
    def deactivate(self, reason: str) -> 'FollowRemoved':
        """
        Deactivate the relationship.
        
        Business context: Used when users unfollow or when policies remove relationships
        """
        if not self.is_active:
            raise ValueError("Relationship is already inactive")
        
        self.is_active = False
        
        return FollowRemoved(
            relationship_id=self.id,
            follower_id=self.follower_id,
            followee_id=self.followee_id,
            removed_at=datetime.now(),
            reason=reason
        )
```

## Repository Testing Strategies

### Testing Repository Implementations

```python
import pytest
from typing import Protocol

class RepositoryTestSuite:
    """
    Shared test suite for all AccountRepository implementations.
    
    This ensures that in-memory, SQL, NoSQL, and other implementations
    all behave consistently from the domain's perspective.
    """
    
    def create_repository(self) -> AccountRepository:
        """Override in concrete test classes"""
        raise NotImplementedError
    
    def test_save_and_retrieve_account(self):
        repo = self.create_repository()
        
        # Create account
        account = Account(
            id=AccountId.new(),
            email=Email("test@example.com"),
            username=Username("testuser")
        )
        
        # Save and retrieve
        repo.save(account)
        retrieved = repo.get_by_id(account.id)
        
        assert retrieved is not None
        assert retrieved.id == account.id
        assert retrieved.email == account.email
        assert retrieved.username == account.username
    
    def test_email_uniqueness_constraint(self):
        repo = self.create_repository()
        
        # Create first account
        account1 = Account(
            id=AccountId.new(),
            email=Email("unique@example.com"),
            username=Username("user1")
        )
        repo.save(account1)
        
        # Try to create second account with same email
        account2 = Account(
            id=AccountId.new(),
            email=Email("unique@example.com"),  # Same email
            username=Username("user2")
        )
        
        with pytest.raises(ValueError, match="Email .* is already taken"):
            repo.save(account2)
    
    def test_update_account_preserves_constraints(self):
        repo = self.create_repository()
        
        # Create and save account
        account = Account(
            id=AccountId.new(),
            email=Email("original@example.com"),
            username=Username("original")
        )
        repo.save(account)
        
        # Block another account (modifying state)
        other_id = AccountId.new()
        account.block_account(other_id)
        
        # Save update
        repo.save(account)
        
        # Verify update persisted
        retrieved = repo.get_by_id(account.id)
        assert retrieved.is_blocked(other_id)

class TestInMemoryAccountRepository(RepositoryTestSuite):
    def create_repository(self) -> AccountRepository:
        return InMemoryAccountRepository()

# Additional implementation-specific tests can be added here
```

## Advanced Repository Patterns

### Unit of Work Pattern

For complex operations that span multiple aggregates:

```python
from typing import List, Protocol
from abc import abstractmethod

class UnitOfWork(Protocol):
    """
    Manages transactions across multiple repositories.
    
    Ensures all changes succeed or fail together.
    """
    
    @abstractmethod
    def register_new(self, entity: object) -> None:
        """Register a new entity to be saved"""
        pass
    
    @abstractmethod
    def register_dirty(self, entity: object) -> None:
        """Register an entity that has been modified"""
        pass
    
    @abstractmethod
    def register_removed(self, entity: object) -> None:
        """Register an entity to be removed"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Save all changes in a single transaction"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Discard all pending changes"""
        pass

class InMemoryUnitOfWork:
    """In-memory implementation of Unit of Work"""
    
    def __init__(self, account_repo: AccountRepository, follow_repo: FollowRepository):
        self.account_repo = account_repo
        self.follow_repo = follow_repo
        self._new_entities: List[object] = []
        self._dirty_entities: List[object] = []
        self._removed_entities: List[object] = []
    
    def register_new(self, entity: object) -> None:
        self._new_entities.append(entity)
    
    def register_dirty(self, entity: object) -> None:
        self._dirty_entities.append(entity)
    
    def register_removed(self, entity: object) -> None:
        self._removed_entities.append(entity)
    
    def commit(self) -> None:
        """Save all changes atomically"""
        try:
            # Save new entities
            for entity in self._new_entities:
                if isinstance(entity, Account):
                    self.account_repo.save(entity)
                elif isinstance(entity, FollowRelationship):
                    self.follow_repo.save_relationship(entity)
            
            # Save dirty entities
            for entity in self._dirty_entities:
                if isinstance(entity, Account):
                    self.account_repo.save(entity)
            
            # Remove entities
            for entity in self._removed_entities:
                if isinstance(entity, FollowRelationship):
                    self.follow_repo.remove_relationship(
                        entity.follower_id, 
                        entity.followee_id
                    )
            
            # Clear pending changes
            self._clear_pending()
            
        except Exception:
            self.rollback()
            raise
    
    def rollback(self) -> None:
        """Discard all pending changes"""
        self._clear_pending()
    
    def _clear_pending(self) -> None:
        self._new_entities.clear()
        self._dirty_entities.clear()
        self._removed_entities.clear()
```

## Real-World Considerations

### Performance Optimization

**Repository Query Optimization:**
```python
class OptimizedAccountRepository:
    """Repository with performance optimizations"""
    
    def get_accounts_with_stats(self, account_ids: List[AccountId]) -> List[AccountWithStats]:
        """
        Bulk operation to avoid N+1 queries.
        
        Returns accounts with their follower/following counts
        """
        # Single query instead of multiple individual queries
        pass
    
    def find_popular_accounts(self, min_followers: int, limit: int) -> List[Account]:
        """
        Find accounts with many followers.
        
        Would use appropriate indexes in database implementation
        """
        pass
```

**Caching Strategies:**
```python
from functools import lru_cache
from typing import Optional

class CachedAccountRepository:
    """Repository with caching layer"""
    
    def __init__(self, underlying_repo: AccountRepository):
        self._repo = underlying_repo
    
    @lru_cache(maxsize=1000)
    def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        """Cache frequently accessed accounts"""
        return self._repo.get_by_id(account_id)
    
    def save(self, account: Account) -> None:
        """Save and invalidate cache"""
        self._repo.save(account)
        # Clear cached entry
        self.get_by_id.cache_clear()
```

### Database Implementation Preview

```python
import sqlite3
from typing import Optional

class SQLiteAccountRepository:
    """SQL implementation of AccountRepository"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self._create_tables()
    
    def _create_tables(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP NOT NULL,
                is_active BOOLEAN NOT NULL,
                blocked_accounts TEXT  -- JSON array of blocked account IDs
            )
        """)
    
    def save(self, account: Account) -> None:
        """Save account with proper SQL error handling"""
        import json
        
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO accounts 
                (id, email, username, created_at, is_active, blocked_accounts)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                account.id.value,
                account.email.value,
                account.username.value,
                account.created_at,
                account.is_active,
                json.dumps([bid.value for bid in account.blocked_accounts])
            ))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                raise ValueError(f"Email {account.email.value} is already taken")
            elif "username" in str(e):
                raise ValueError(f"Username {account.username.value} is already taken")
            raise
    
    def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        """Retrieve account and reconstitute domain object"""
        cursor = self.conn.execute(
            "SELECT * FROM accounts WHERE id = ?", 
            (account_id.value,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_account(row)
    
    def _row_to_account(self, row) -> Account:
        """Convert database row to domain object"""
        import json
        
        blocked_ids = {AccountId(bid) for bid in json.loads(row['blocked_accounts'] or '[]')}
        
        return Account(
            id=AccountId(row['id']),
            email=Email(row['email']),
            username=Username(row['username']),
            created_at=row['created_at'],
            is_active=bool(row['is_active']),
            blocked_accounts=blocked_ids
        )
```

## Summary: Domain-Driven Persistence

Repositories and Aggregates work together to create persistence that serves the domain:

🎯 **Repositories hide persistence complexity** behind domain-focused interfaces
🎯 **Aggregates define consistency boundaries** that make business sense
🎯 **In-memory implementations** enable fast development and testing
🎯 **Interface-based design** allows swapping implementations easily
🎯 **Domain needs drive repository design**, not database structure

**Key Design Principles:**
- **Think in terms of collections**, not database tables
- **Design interfaces from business perspective**, not technical perspective
- **Keep aggregates small** for better performance and maintainability
- **One repository per aggregate root** to maintain boundaries
- **Start with in-memory implementations** and evolve to databases when needed

In our social media platform, we've established:
- **Account aggregate** managing identity and blocking relationships
- **FollowRelationship aggregate** managing social connections
- **Domain-focused repositories** that express business operations naturally
- **In-memory implementations** perfect for development and testing

This foundation supports the complex business policies we'll implement in Part 4, while keeping persistence concerns separate from domain logic.

---

**Next:** [Part 4 - Commands, Handlers, Events, Policies](/courses/04-commands-handlers-events-policies/) - Learn to implement business workflows and cross-aggregate policies using command patterns and event-driven architecture.
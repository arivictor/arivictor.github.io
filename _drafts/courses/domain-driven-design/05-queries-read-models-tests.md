---
layout: course
title: "DDD Workshop Part 5: Queries, Read Models, Tests"
part: "Part 5 of 5"
duration: "90 minutes"
prev_course: "/courses/04-commands-handlers-events-policies/"
prev_title: "Commands, Handlers, Events, Policies"
order: 5
---

# Queries, Read Models, and Tests: Completing the DDD Architecture

**Goal:** Build optimized read models that serve application needs, implement comprehensive testing strategies that validate business logic, and create production-ready DDD applications with proper separation of concerns.

## Introduction: The Query Side of CQRS

In Part 4, we built the **command side** of our CQRS architecture - focused on changing state through commands, handlers, and events. Now we complete the picture with the **query side** - optimized for reading data and serving user interfaces.

**Why separate read and write models?**

**Write Model Challenges:**
- Optimized for consistency and business rule enforcement
- Complex aggregate boundaries make simple queries difficult
- Normalization makes joins expensive
- Business logic creates complexity for simple data access

**Read Model Benefits:**
- Optimized for specific query patterns
- Denormalized for fast access
- No business logic complexity
- Can use different storage technologies
- Scales independently from write side

This separation allows us to optimize each side for its specific needs without compromise.

## CQRS: Command Query Responsibility Segregation

### The Complete Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Write Side    │         │   Read Side     │
│                 │         │                 │
│ Commands ──────►│         │ Queries ──────►│
│ Handlers        │  Events │ Read Models     │
│ Aggregates      │────────►│ Projections     │
│ Repositories    │         │ Query Handlers  │
│                 │         │                 │
└─────────────────┘         └─────────────────┘
```

**Data Flow:**
1. **Commands** change state through aggregates
2. **Events** are published describing what happened
3. **Projections** listen to events and update read models
4. **Queries** read from optimized read models
5. **User interfaces** display data from read models

### Benefits of This Architecture

🎯 **Independent optimization**: Reads and writes can use different technologies
🎯 **Better performance**: Read models are optimized for specific queries
🎯 **Simpler queries**: No complex joins or business logic
🎯 **Eventual consistency**: Acceptable for most read scenarios
🎯 **Scalability**: Can scale reads and writes independently

## Read Model Design Principles

### 1. Purpose-Built for Specific Queries

Don't create generic read models. Build them for specific UI needs:

```python
# ❌ Generic read model
@dataclass
class AccountReadModel:
    id: str
    email: str
    username: str
    created_at: datetime
    is_active: bool
    blocked_accounts: List[str]
    # ... everything from write model

# ✅ Purpose-built read models  
@dataclass
class AccountProfile:
    """For profile display pages"""
    id: str
    username: str
    display_name: str
    follower_count: int
    following_count: int
    is_verified: bool

@dataclass
class AccountSummary:
    """For account listings and searches"""
    id: str
    username: str
    display_name: str
    follower_count: int

@dataclass
class RelationshipStatus:
    """For relationship queries between two users"""
    user_a_follows_user_b: bool
    user_b_follows_user_a: bool
    user_a_blocked_by_user_b: bool
    user_b_blocked_by_user_a: bool
    are_mutual_followers: bool
```

### 2. Denormalized for Query Performance

Read models should contain all data needed for a query without joins:

```python
@dataclass
class UserFeedItem:
    """Denormalized for feed display"""
    post_id: str
    author_id: str
    author_username: str
    author_display_name: str
    author_avatar_url: str
    content: str
    created_at: datetime
    like_count: int
    comment_count: int
    user_has_liked: bool  # Specific to requesting user
    user_can_comment: bool  # Based on relationship status
```

### 3. Eventual Consistency is Acceptable

Read models don't need immediate consistency. They can be updated asynchronously:

```python
class ReadModelProjector:
    """Updates read models based on events"""
    
    def project_account_registered(self, event: AccountRegistered) -> None:
        """Create initial read model entries"""
        profile = AccountProfile(
            id=event.account_id.value,
            username=event.username.value,
            display_name=event.username.value,  # Default to username
            follower_count=0,
            following_count=0,
            is_verified=False
        )
        self.profile_store.save(profile)
    
    def project_follow_created(self, event: FollowCreated) -> None:
        """Update follower/following counts"""
        # Update follower count
        followee_profile = self.profile_store.get(event.followee_id.value)
        if followee_profile:
            followee_profile.follower_count += 1
            self.profile_store.save(followee_profile)
        
        # Update following count
        follower_profile = self.profile_store.get(event.follower_id.value)
        if follower_profile:
            follower_profile.following_count += 1
            self.profile_store.save(follower_profile)
```

## Implementing Read Models

### In-Memory Read Model Store

Perfect for development and testing:

```python
from typing import Dict, List, Optional, Callable, TypeVar
from collections import defaultdict

T = TypeVar('T')

class InMemoryReadModelStore:
    """
    Generic in-memory store for read models.
    
    Features:
    - Type-safe storage and retrieval
    - Indexing for fast queries
    - Bulk operations for efficiency
    """
    
    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, any]] = defaultdict(dict)
        self._indexes: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    
    def save(self, model_type: str, model_id: str, model: T) -> None:
        """Save a read model with automatic indexing"""
        self._data[model_type][model_id] = model
        self._update_indexes(model_type, model_id, model)
    
    def get(self, model_type: str, model_id: str) -> Optional[T]:
        """Get a read model by ID"""
        return self._data[model_type].get(model_id)
    
    def find_by_index(self, model_type: str, index_name: str, index_value: str) -> List[T]:
        """Find read models by indexed field"""
        model_ids = self._indexes[model_type][f"{index_name}:{index_value}"]
        return [self._data[model_type][mid] for mid in model_ids if mid in self._data[model_type]]
    
    def query(self, model_type: str, predicate: Callable[[T], bool]) -> List[T]:
        """Query read models with a predicate function"""
        return [model for model in self._data[model_type].values() if predicate(model)]
    
    def _update_indexes(self, model_type: str, model_id: str, model: any) -> None:
        """Update indexes for a model"""
        # Remove from existing indexes
        for index_key in list(self._indexes[model_type].keys()):
            if model_id in self._indexes[model_type][index_key]:
                self._indexes[model_type][index_key].remove(model_id)
        
        # Add to new indexes based on model attributes
        if hasattr(model, 'username'):
            self._indexes[model_type][f"username:{model.username}"].append(model_id)
        if hasattr(model, 'email'):
            self._indexes[model_type][f"email:{model.email}"].append(model_id)
```

### Account Profile Read Model

```python
from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class AccountProfileReadModel:
    """Read model optimized for profile display"""
    id: str
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    post_count: int
    is_verified: bool
    is_active: bool
    joined_date: datetime
    last_active: Optional[datetime] = None

class AccountProfileStore:
    """Specialized store for account profiles"""
    
    def __init__(self, store: InMemoryReadModelStore):
        self._store = store
        self._model_type = "account_profile"
    
    def save(self, profile: AccountProfileReadModel) -> None:
        self._store.save(self._model_type, profile.id, profile)
    
    def get_by_id(self, account_id: str) -> Optional[AccountProfileReadModel]:
        return self._store.get(self._model_type, account_id)
    
    def get_by_username(self, username: str) -> Optional[AccountProfileReadModel]:
        results = self._store.find_by_index(self._model_type, "username", username)
        return results[0] if results else None
    
    def search_by_username_prefix(self, prefix: str, limit: int = 10) -> List[AccountProfileReadModel]:
        """Search for usernames starting with prefix"""
        all_profiles = self._store.query(
            self._model_type,
            lambda p: p.username.lower().startswith(prefix.lower()) and p.is_active
        )
        # Sort by follower count (popularity)
        all_profiles.sort(key=lambda p: p.follower_count, reverse=True)
        return all_profiles[:limit]
    
    def get_popular_accounts(self, limit: int = 20) -> List[AccountProfileReadModel]:
        """Get most popular accounts by follower count"""
        all_profiles = self._store.query(self._model_type, lambda p: p.is_active)
        all_profiles.sort(key=lambda p: p.follower_count, reverse=True)
        return all_profiles[:limit]
```

### Relationship Read Model

```python
@dataclass
class RelationshipReadModel:
    """Read model for relationship queries between two users"""
    user_a_id: str
    user_b_id: str
    a_follows_b: bool
    b_follows_a: bool
    a_blocked_by_b: bool
    b_blocked_by_a: bool
    relationship_type: str  # "mutual", "one_way", "blocked", "none"
    last_updated: datetime

class RelationshipStore:
    """Store for relationship read models"""
    
    def __init__(self, store: InMemoryReadModelStore):
        self._store = store
        self._model_type = "relationship"
    
    def save(self, relationship: RelationshipReadModel) -> None:
        # Use consistent ordering for relationship ID
        key = self._make_key(relationship.user_a_id, relationship.user_b_id)
        self._store.save(self._model_type, key, relationship)
    
    def get_relationship(self, user_a_id: str, user_b_id: str) -> Optional[RelationshipReadModel]:
        key = self._make_key(user_a_id, user_b_id)
        return self._store.get(self._model_type, key)
    
    def get_followers(self, user_id: str) -> List[str]:
        """Get all users following the given user"""
        relationships = self._store.query(
            self._model_type,
            lambda r: (r.user_b_id == user_id and r.a_follows_b) or 
                     (r.user_a_id == user_id and r.b_follows_a)
        )
        followers = []
        for rel in relationships:
            if rel.user_b_id == user_id and rel.a_follows_b:
                followers.append(rel.user_a_id)
            elif rel.user_a_id == user_id and rel.b_follows_a:
                followers.append(rel.user_b_id)
        return followers
    
    def get_following(self, user_id: str) -> List[str]:
        """Get all users the given user is following"""
        relationships = self._store.query(
            self._model_type,
            lambda r: (r.user_a_id == user_id and r.a_follows_b) or 
                     (r.user_b_id == user_id and r.b_follows_a)
        )
        following = []
        for rel in relationships:
            if rel.user_a_id == user_id and rel.a_follows_b:
                following.append(rel.user_b_id)
            elif rel.user_b_id == user_id and rel.b_follows_a:
                following.append(rel.user_a_id)
        return following
    
    def _make_key(self, user_a_id: str, user_b_id: str) -> str:
        """Create consistent key for relationship pairs"""
        # Always put smaller ID first for consistency
        if user_a_id < user_b_id:
            return f"{user_a_id}:{user_b_id}"
        else:
            return f"{user_b_id}:{user_a_id}"
```

## Event Projections: Keeping Read Models Current

Projections listen to domain events and update read models accordingly:

```python
class ReadModelProjector:
    """
    Projects domain events into read models.
    
    Responsibilities:
    - Listen to all relevant domain events
    - Update read models to reflect state changes
    - Maintain derived data (counts, relationships)
    - Handle event replay for read model rebuilding
    """
    
    def __init__(self, profile_store: AccountProfileStore, relationship_store: RelationshipStore):
        self.profiles = profile_store
        self.relationships = relationship_store
        self._event_handlers = {
            AccountRegistered: self._project_account_registered,
            FollowCreated: self._project_follow_created,
            FollowRemoved: self._project_follow_removed,
            AccountBlocked: self._project_account_blocked,
            AccountDeactivated: self._project_account_deactivated,
        }
    
    def project(self, event: Event) -> None:
        """Project a single event into read models"""
        handler = self._event_handlers.get(type(event))
        if handler:
            handler(event)
    
    def project_all(self, events: List[Event]) -> None:
        """Project multiple events efficiently"""
        for event in events:
            self.project(event)
    
    def _project_account_registered(self, event: AccountRegistered) -> None:
        """Create initial profile read model"""
        profile = AccountProfileReadModel(
            id=event.account_id.value,
            username=event.username.value,
            display_name=event.username.value,  # Default to username
            bio="",
            follower_count=0,
            following_count=0,
            post_count=0,
            is_verified=False,
            is_active=True,
            joined_date=event.registered_at
        )
        self.profiles.save(profile)
    
    def _project_follow_created(self, event: FollowCreated) -> None:
        """Update follower/following counts and relationship status"""
        follower_id = event.follower_id.value
        followee_id = event.followee_id.value
        
        # Update follower count
        followee_profile = self.profiles.get_by_id(followee_id)
        if followee_profile:
            followee_profile.follower_count += 1
            self.profiles.save(followee_profile)
        
        # Update following count
        follower_profile = self.profiles.get_by_id(follower_id)
        if follower_profile:
            follower_profile.following_count += 1
            self.profiles.save(follower_profile)
        
        # Update relationship model
        self._update_relationship(follower_id, followee_id, follow_created=True)
    
    def _project_follow_removed(self, event: FollowRemoved) -> None:
        """Update counts when follow relationship is removed"""
        follower_id = event.follower_id.value
        followee_id = event.followee_id.value
        
        # Update follower count
        followee_profile = self.profiles.get_by_id(followee_id)
        if followee_profile and followee_profile.follower_count > 0:
            followee_profile.follower_count -= 1
            self.profiles.save(followee_profile)
        
        # Update following count
        follower_profile = self.profiles.get_by_id(follower_id)
        if follower_profile and follower_profile.following_count > 0:
            follower_profile.following_count -= 1
            self.profiles.save(follower_profile)
        
        # Update relationship model
        self._update_relationship(follower_id, followee_id, follow_removed=True)
    
    def _project_account_blocked(self, event: AccountBlocked) -> None:
        """Update relationship when blocking occurs"""
        blocker_id = event.blocker_id.value
        blocked_id = event.blocked_id.value
        
        self._update_relationship(blocker_id, blocked_id, blocking_created=True)
    
    def _project_account_deactivated(self, event: AccountDeactivated) -> None:
        """Mark account as inactive"""
        profile = self.profiles.get_by_id(event.account_id.value)
        if profile:
            profile.is_active = False
            self.profiles.save(profile)
    
    def _update_relationship(self, user_a_id: str, user_b_id: str, 
                           follow_created: bool = False, follow_removed: bool = False,
                           blocking_created: bool = False) -> None:
        """Update relationship read model"""
        existing = self.relationships.get_relationship(user_a_id, user_b_id)
        
        if not existing:
            # Create new relationship
            relationship = RelationshipReadModel(
                user_a_id=user_a_id,
                user_b_id=user_b_id,
                a_follows_b=False,
                b_follows_a=False,
                a_blocked_by_b=False,
                b_blocked_by_a=False,
                relationship_type="none",
                last_updated=datetime.now()
            )
        else:
            relationship = existing
        
        # Update based on event
        if follow_created:
            if relationship.user_a_id == user_a_id:
                relationship.a_follows_b = True
            else:
                relationship.b_follows_a = True
        
        if follow_removed:
            if relationship.user_a_id == user_a_id:
                relationship.a_follows_b = False
            else:
                relationship.b_follows_a = False
        
        if blocking_created:
            if relationship.user_a_id == user_a_id:
                relationship.b_blocked_by_a = True
            else:
                relationship.a_blocked_by_b = True
        
        # Determine relationship type
        relationship.relationship_type = self._determine_relationship_type(relationship)
        relationship.last_updated = datetime.now()
        
        self.relationships.save(relationship)
    
    def _determine_relationship_type(self, rel: RelationshipReadModel) -> str:
        """Determine the overall relationship type"""
        if rel.a_blocked_by_b or rel.b_blocked_by_a:
            return "blocked"
        elif rel.a_follows_b and rel.b_follows_a:
            return "mutual"
        elif rel.a_follows_b or rel.b_follows_a:
            return "one_way"
        else:
            return "none"
```

## Query Handlers: Serving Application Needs

Query handlers provide clean interfaces for reading data:

```python
class AccountQueryHandler:
    """Handles queries related to accounts and profiles"""
    
    def __init__(self, profile_store: AccountProfileStore, relationship_store: RelationshipStore):
        self.profiles = profile_store
        self.relationships = relationship_store
    
    def get_profile(self, account_id: str) -> Optional[AccountProfileReadModel]:
        """Get full profile for an account"""
        return self.profiles.get_by_id(account_id)
    
    def search_accounts(self, query: str, limit: int = 10) -> List[AccountProfileReadModel]:
        """Search accounts by username prefix"""
        return self.profiles.search_by_username_prefix(query, limit)
    
    def get_popular_accounts(self, limit: int = 20) -> List[AccountProfileReadModel]:
        """Get most popular accounts"""
        return self.profiles.get_popular_accounts(limit)
    
    def get_relationship_status(self, user_id: str, other_user_id: str) -> RelationshipReadModel:
        """Get relationship status between two users"""
        relationship = self.relationships.get_relationship(user_id, other_user_id)
        
        if not relationship:
            # Return default "no relationship" status
            return RelationshipReadModel(
                user_a_id=user_id,
                user_b_id=other_user_id,
                a_follows_b=False,
                b_follows_a=False,
                a_blocked_by_b=False,
                b_blocked_by_a=False,
                relationship_type="none",
                last_updated=datetime.now()
            )
        
        return relationship
    
    def get_followers(self, account_id: str) -> List[AccountProfileReadModel]:
        """Get follower profiles"""
        follower_ids = self.relationships.get_followers(account_id)
        return [self.profiles.get_by_id(fid) for fid in follower_ids 
                if self.profiles.get_by_id(fid)]
    
    def get_following(self, account_id: str) -> List[AccountProfileReadModel]:
        """Get following profiles"""
        following_ids = self.relationships.get_following(account_id)
        return [self.profiles.get_by_id(fid) for fid in following_ids 
                if self.profiles.get_by_id(fid)]

class SocialGraphQueryHandler:
    """Handles complex social graph queries"""
    
    def __init__(self, relationship_store: RelationshipStore, profile_store: AccountProfileStore):
        self.relationships = relationship_store
        self.profiles = profile_store
    
    def get_mutual_connections(self, user_id: str) -> List[AccountProfileReadModel]:
        """Get accounts that both follow and are followed by the user"""
        all_relationships = self.relationships._store.query(
            "relationship",
            lambda r: (r.user_a_id == user_id or r.user_b_id == user_id) and
                     r.relationship_type == "mutual"
        )
        
        mutual_user_ids = []
        for rel in all_relationships:
            other_user_id = rel.user_b_id if rel.user_a_id == user_id else rel.user_a_id
            mutual_user_ids.append(other_user_id)
        
        return [self.profiles.get_by_id(uid) for uid in mutual_user_ids 
                if self.profiles.get_by_id(uid)]
    
    def suggest_connections(self, user_id: str, limit: int = 10) -> List[AccountProfileReadModel]:
        """Suggest new connections based on mutual follows"""
        # Get users followed by people this user follows
        following = self.relationships.get_following(user_id)
        suggestions = set()
        
        for followed_user_id in following:
            # Get who they follow
            their_following = self.relationships.get_following(followed_user_id)
            for suggestion_id in their_following:
                if (suggestion_id != user_id and 
                    suggestion_id not in following and
                    not self._is_blocked_relationship(user_id, suggestion_id)):
                    suggestions.add(suggestion_id)
        
        # Convert to profiles and sort by popularity
        suggestion_profiles = [self.profiles.get_by_id(sid) for sid in suggestions 
                             if self.profiles.get_by_id(sid)]
        suggestion_profiles.sort(key=lambda p: p.follower_count, reverse=True)
        
        return suggestion_profiles[:limit]
    
    def _is_blocked_relationship(self, user_a_id: str, user_b_id: str) -> bool:
        """Check if there's a blocking relationship"""
        rel = self.relationships.get_relationship(user_a_id, user_b_id)
        return rel and rel.relationship_type == "blocked"
```

## Comprehensive Testing Strategy

### Testing Domain Logic

```python
import pytest
from datetime import datetime

class TestDomainLogic:
    """Test core domain behavior in isolation"""
    
    def test_account_creation(self):
        """Test account aggregate creation"""
        email = Email("test@example.com")
        username = Username("testuser")
        
        account, event = Account.register(email, username)
        
        assert account.email == email
        assert account.username == username
        assert account.is_active
        assert isinstance(event, AccountRegistered)
        assert event.account_id == account.id
    
    def test_account_blocking_business_rules(self):
        """Test blocking business rules"""
        account = Account(
            id=AccountId.new(),
            email=Email("test@example.com"),
            username=Username("testuser")
        )
        other_id = AccountId.new()
        
        # Test blocking
        event = account.block_account(other_id)
        assert isinstance(event, AccountBlocked)
        assert account.is_blocked(other_id)
        
        # Test cannot block self
        with pytest.raises(ValueError, match="Cannot block yourself"):
            account.block_account(account.id)
    
    def test_value_object_validation(self):
        """Test value object business rules"""
        # Valid email
        email = Email("valid@example.com")
        assert email.value == "valid@example.com"
        
        # Invalid email
        with pytest.raises(ValueError):
            Email("invalid-email")
        
        # Username validation
        valid_username = Username("valid_user_123")
        assert valid_username.value == "valid_user_123"
        
        # Invalid username
        with pytest.raises(ValueError):
            Username("invalid-username-too-long-and-contains-hyphens")

class TestCommandHandlers:
    """Test command handling logic"""
    
    def setup_method(self):
        self.account_repo = InMemoryAccountRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.app = SocialMediaApplication(self.account_repo, self.follow_repo)
    
    def test_successful_registration(self):
        """Test successful account registration"""
        cmd = RegisterAccount(
            email=Email("new@example.com"),
            username=Username("newuser")
        )
        
        events = self.app.handle(cmd)
        
        assert len(events) == 1
        assert isinstance(events[0], AccountRegistered)
        
        # Verify account was saved
        account = self.account_repo.get_by_email(Email("new@example.com"))
        assert account is not None
        assert account.username.value == "newuser"
    
    def test_duplicate_email_registration(self):
        """Test registration fails with duplicate email"""
        email = Email("duplicate@example.com")
        
        # Register first account
        self.app.handle(RegisterAccount(email, Username("user1")))
        
        # Try to register with same email
        events = self.app.handle(RegisterAccount(email, Username("user2")))
        
        assert len(events) == 1
        assert isinstance(events[0], AccountRegistrationFailed)
        assert "Email already registered" in events[0].reason
    
    def test_follow_workflow(self):
        """Test complete follow workflow"""
        # Create two accounts
        alice_events = self.app.handle(RegisterAccount(
            Email("alice@example.com"), Username("alice")
        ))
        bob_events = self.app.handle(RegisterAccount(
            Email("bob@example.com"), Username("bob")
        ))
        
        alice_id = alice_events[0].account_id
        bob_id = bob_events[0].account_id
        
        # Alice follows Bob
        follow_events = self.app.handle(FollowAccount(alice_id, bob_id))
        
        assert len(follow_events) == 1
        assert isinstance(follow_events[0], FollowCreated)
        assert self.follow_repo.exists(alice_id, bob_id)
    
    def test_blocking_policy_integration(self):
        """Test that blocking automatically removes follows"""
        # Setup accounts with follow relationship
        alice_events = self.app.handle(RegisterAccount(
            Email("alice@example.com"), Username("alice")
        ))
        bob_events = self.app.handle(RegisterAccount(
            Email("bob@example.com"), Username("bob")
        ))
        
        alice_id = alice_events[0].account_id
        bob_id = bob_events[0].account_id
        
        # Create mutual follows
        self.app.handle(FollowAccount(alice_id, bob_id))
        self.app.handle(FollowAccount(bob_id, alice_id))
        
        assert self.follow_repo.exists(alice_id, bob_id)
        assert self.follow_repo.exists(bob_id, alice_id)
        
        # Bob blocks Alice
        self.app.handle(BlockAccount(bob_id, alice_id))
        
        # Policy should have removed both follow relationships
        assert not self.follow_repo.exists(alice_id, bob_id)
        assert not self.follow_repo.exists(bob_id, alice_id)

class TestReadModels:
    """Test read model projections and queries"""
    
    def setup_method(self):
        self.store = InMemoryReadModelStore()
        self.profile_store = AccountProfileStore(self.store)
        self.relationship_store = RelationshipStore(self.store)
        self.projector = ReadModelProjector(self.profile_store, self.relationship_store)
        self.query_handler = AccountQueryHandler(self.profile_store, self.relationship_store)
    
    def test_account_registration_projection(self):
        """Test that account registration creates profile read model"""
        event = AccountRegistered(
            account_id=AccountId.new(),
            email=Email("test@example.com"),
            username=Username("testuser"),
            registered_at=datetime.now()
        )
        
        self.projector.project(event)
        
        profile = self.profile_store.get_by_id(event.account_id.value)
        assert profile is not None
        assert profile.username == "testuser"
        assert profile.follower_count == 0
        assert profile.following_count == 0
    
    def test_follow_projection_updates_counts(self):
        """Test that follow events update follower/following counts"""
        # Create profiles
        alice_id = AccountId.new()
        bob_id = AccountId.new()
        
        self.projector.project(AccountRegistered(
            alice_id, Email("alice@example.com"), Username("alice"), datetime.now()
        ))
        self.projector.project(AccountRegistered(
            bob_id, Email("bob@example.com"), Username("bob"), datetime.now()
        ))
        
        # Project follow event
        follow_event = FollowCreated(
            relationship_id=FollowRelationshipId.new(),
            follower_id=alice_id,
            followee_id=bob_id,
            created_at=datetime.now()
        )
        self.projector.project(follow_event)
        
        # Check counts updated
        alice_profile = self.profile_store.get_by_id(alice_id.value)
        bob_profile = self.profile_store.get_by_id(bob_id.value)
        
        assert alice_profile.following_count == 1
        assert bob_profile.follower_count == 1
    
    def test_relationship_query(self):
        """Test relationship status queries"""
        # Setup relationship
        alice_id = AccountId.new()
        bob_id = AccountId.new()
        
        relationship = RelationshipReadModel(
            user_a_id=alice_id.value,
            user_b_id=bob_id.value,
            a_follows_b=True,
            b_follows_a=False,
            a_blocked_by_b=False,
            b_blocked_by_a=False,
            relationship_type="one_way",
            last_updated=datetime.now()
        )
        self.relationship_store.save(relationship)
        
        # Query relationship
        result = self.query_handler.get_relationship_status(alice_id.value, bob_id.value)
        assert result.a_follows_b == True
        assert result.b_follows_a == False
        assert result.relationship_type == "one_way"

class TestIntegrationScenarios:
    """Test complete business scenarios end-to-end"""
    
    def setup_method(self):
        # Setup complete system
        self.account_repo = InMemoryAccountRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.app = SocialMediaApplication(self.account_repo, self.follow_repo)
        
        # Setup read models
        self.read_store = InMemoryReadModelStore()
        self.profile_store = AccountProfileStore(self.read_store)
        self.relationship_store = RelationshipStore(self.read_store)
        self.projector = ReadModelProjector(self.profile_store, self.relationship_store)
        self.query_handler = AccountQueryHandler(self.profile_store, self.relationship_store)
        
        # Connect projector to event bus
        self.app.event_bus.subscribe(AccountRegistered, self.projector.project)
        self.app.event_bus.subscribe(FollowCreated, self.projector.project)
        self.app.event_bus.subscribe(FollowRemoved, self.projector.project)
        self.app.event_bus.subscribe(AccountBlocked, self.projector.project)
    
    def test_complete_social_interaction_scenario(self):
        """Test a complete social media interaction scenario"""
        # 1. Alice and Bob register
        alice_events = self.app.handle(RegisterAccount(
            Email("alice@example.com"), Username("alice")
        ))
        bob_events = self.app.handle(RegisterAccount(
            Email("bob@example.com"), Username("bob")
        ))
        
        alice_id = alice_events[0].account_id
        bob_id = bob_events[0].account_id
        
        # Verify profiles created
        alice_profile = self.query_handler.get_profile(alice_id.value)
        bob_profile = self.query_handler.get_profile(bob_id.value)
        
        assert alice_profile.username == "alice"
        assert bob_profile.username == "bob"
        assert alice_profile.follower_count == 0
        assert alice_profile.following_count == 0
        
        # 2. Alice follows Bob
        self.app.handle(FollowAccount(alice_id, bob_id))
        
        # Verify counts updated
        alice_profile = self.query_handler.get_profile(alice_id.value)
        bob_profile = self.query_handler.get_profile(bob_id.value)
        
        assert alice_profile.following_count == 1
        assert bob_profile.follower_count == 1
        
        # Verify relationship status
        relationship = self.query_handler.get_relationship_status(alice_id.value, bob_id.value)
        assert relationship.a_follows_b == True
        assert relationship.b_follows_a == False
        assert relationship.relationship_type == "one_way"
        
        # 3. Bob blocks Alice (this should remove the follow)
        self.app.handle(BlockAccount(bob_id, alice_id))
        
        # Verify follow was removed by policy
        relationship = self.query_handler.get_relationship_status(alice_id.value, bob_id.value)
        assert relationship.a_follows_b == False
        assert relationship.relationship_type == "blocked"
        
        # Verify counts updated
        alice_profile = self.query_handler.get_profile(alice_id.value)
        bob_profile = self.query_handler.get_profile(bob_id.value)
        
        assert alice_profile.following_count == 0
        assert bob_profile.follower_count == 0
    
    def test_search_and_discovery_features(self):
        """Test search and discovery functionality"""
        # Create several accounts
        accounts = [
            ("alice@example.com", "alice_smith"),
            ("bob@example.com", "bob_jones"),
            ("charlie@example.com", "alice_wilson"),
            ("diana@example.com", "diana_alice"),
        ]
        
        account_ids = []
        for email, username in accounts:
            events = self.app.handle(RegisterAccount(Email(email), Username(username)))
            account_ids.append(events[0].account_id)
        
        # Test username search
        alice_results = self.query_handler.search_accounts("alice", limit=10)
        assert len(alice_results) == 3  # alice_smith, alice_wilson, diana_alice
        
        # Test exact username lookup
        alice_smith = self.profile_store.get_by_username("alice_smith")
        assert alice_smith is not None
        assert alice_smith.username == "alice_smith"
```

## Production Considerations

### Database Integration

```python
import sqlite3
import json
from typing import Optional, List

class SQLiteReadModelStore:
    """SQL implementation for production use"""
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS account_profiles (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                display_name TEXT,
                bio TEXT,
                follower_count INTEGER,
                following_count INTEGER,
                post_count INTEGER,
                is_verified BOOLEAN,
                is_active BOOLEAN,
                joined_date TIMESTAMP,
                last_active TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                user_a_id TEXT,
                user_b_id TEXT,
                a_follows_b BOOLEAN,
                b_follows_a BOOLEAN,
                a_blocked_by_b BOOLEAN,
                b_blocked_by_a BOOLEAN,
                relationship_type TEXT,
                last_updated TIMESTAMP,
                UNIQUE(user_a_id, user_b_id)
            )
        """)
        
        # Create indexes for performance
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON account_profiles(username)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_follower_count ON account_profiles(follower_count DESC)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_relationship_users ON relationships(user_a_id, user_b_id)")
        
        self.conn.commit()
```

### Event Sourcing Integration

```python
class EventSourcedReadModelProjector:
    """Read model projector that can rebuild from event streams"""
    
    def __init__(self, profile_store: AccountProfileStore, relationship_store: RelationshipStore):
        self.profiles = profile_store
        self.relationships = relationship_store
        self._last_processed_event = 0
    
    def rebuild_from_events(self, event_stream: List[Event]) -> None:
        """Rebuild all read models from event stream"""
        # Clear existing read models
        self._clear_all_read_models()
        
        # Process all events in order
        for event in event_stream:
            self.project(event)
        
        self._last_processed_event = len(event_stream)
    
    def process_new_events(self, event_stream: List[Event]) -> None:
        """Process only new events since last checkpoint"""
        new_events = event_stream[self._last_processed_event:]
        
        for event in new_events:
            self.project(event)
        
        self._last_processed_event = len(event_stream)
    
    def _clear_all_read_models(self) -> None:
        """Clear all read models for rebuilding"""
        # Implementation depends on storage mechanism
        pass
```

### Monitoring and Observability

```python
import time
from typing import Dict
from collections import defaultdict

class InstrumentedQueryHandler:
    """Query handler with performance monitoring"""
    
    def __init__(self, delegate: AccountQueryHandler):
        self._delegate = delegate
        self._query_counts: Dict[str, int] = defaultdict(int)
        self._query_times: Dict[str, List[float]] = defaultdict(list)
    
    def get_profile(self, account_id: str) -> Optional[AccountProfileReadModel]:
        return self._instrument("get_profile", lambda: self._delegate.get_profile(account_id))
    
    def search_accounts(self, query: str, limit: int = 10) -> List[AccountProfileReadModel]:
        return self._instrument("search_accounts", 
                               lambda: self._delegate.search_accounts(query, limit))
    
    def _instrument(self, operation: str, func):
        """Instrument a query operation"""
        start_time = time.time()
        try:
            result = func()
            self._query_counts[operation] += 1
            execution_time = time.time() - start_time
            self._query_times[operation].append(execution_time)
            return result
        except Exception as e:
            # Log error metrics
            self._query_counts[f"{operation}_error"] += 1
            raise
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        metrics = {}
        for operation, times in self._query_times.items():
            if times:
                metrics[operation] = {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "max_time": max(times),
                    "min_time": min(times)
                }
        return metrics
```

## Summary: Complete DDD Architecture

We've now built a complete Domain-Driven Design architecture with:

🎯 **Rich domain models** with entities and value objects that encapsulate business logic
🎯 **Command-based operations** that follow consistent patterns and generate events
🎯 **Event-driven policies** that maintain consistency across aggregate boundaries  
🎯 **Optimized read models** that serve specific query needs efficiently
🎯 **Comprehensive testing** that validates business logic at all levels
🎯 **Production-ready patterns** for scaling and monitoring

### The Complete Architecture

```
┌─────────────────────────────────────────────────┐
│                 Application Layer                │
│  ┌─────────────────┐    ┌─────────────────┐    │
│  │  Command Side   │    │   Query Side    │    │
│  │                 │    │                 │    │
│  │ • Commands      │    │ • Query Handlers│    │
│  │ • Handlers      │    │ • Read Models   │    │
│  │ • Policies      │    │ • Projections   │    │
│  └─────────────────┘    └─────────────────┘    │
└─────────────────────────────────────────────────┘
                    │
                 Events
                    │
┌─────────────────────────────────────────────────┐
│                 Domain Layer                     │
│                                                 │
│ • Value Objects  • Entities  • Aggregates      │
│ • Domain Events  • Business Rules              │
│                                                 │
└─────────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────────┐
│               Infrastructure Layer               │
│                                                 │
│ • Repositories  • Event Bus  • Persistence     │
│ • External APIs  • Messaging  • Monitoring     │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Key Benefits Achieved

**Business Alignment:**
- Ubiquitous language shared between business and technical teams
- Domain concepts clearly expressed in code
- Business rules centralized in domain objects

**Technical Excellence:**
- Clear separation of concerns across layers
- Testable architecture with fast, reliable tests
- Scalable read and write sides optimized for their purposes
- Event-driven architecture enabling reactive systems

**Maintainability:**
- Changes to business rules isolated in domain layer
- New features added through new command handlers and projections
- Read models evolved independently of write models
- Comprehensive test coverage ensuring confidence in changes

### Real-World Application

This architecture has successfully solved our original problem: **the blocked user visibility bug**. When a user blocks another user, the policy automatically removes all follow relationships, ensuring that blocked users cannot see each other's content.

More importantly, we've created a foundation that can evolve with changing business requirements while maintaining technical excellence and business alignment.

**Congratulations on completing the comprehensive Domain-Driven Design course!**

You now have the knowledge and practical experience to:
- ✅ **Discover domain complexity** through event storming
- ✅ **Model complex business logic** with entities, value objects, and aggregates
- ✅ **Design persistence** that serves the domain rather than constraining it
- ✅ **Implement robust workflows** through commands, handlers, and policies
- ✅ **Build optimized query systems** with read models and projections
- ✅ **Test domain logic comprehensively** at all architectural layers
- ✅ **Scale systems** through CQRS and event-driven architecture

Take these patterns and apply them to your own domain challenges. Remember: start simple, focus on the core domain complexity, and evolve the architecture as you learn more about the business needs.

---

**Want to continue learning?** Explore advanced DDD patterns like event sourcing, context mapping, and distributed domain modeling to tackle even more complex business challenges.
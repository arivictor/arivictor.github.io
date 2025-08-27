---
layout: course
title: "DDD Workshop Part 4: Commands, Handlers, Events, Policies"
part: "Part 4 of 5"
duration: "90 minutes"
prev_course: "/courses/03-repositories-aggregates/"
prev_title: "Repositories and Aggregates"
next_course: "/courses/05-queries-read-models-tests/"
next_title: "Queries, Read Models, Tests"
order: 4
---

# Commands, Handlers, Events, and Policies: Orchestrating Business Workflows

**Goal:** Implement robust business workflows using the Command pattern, create event-driven policies that maintain consistency across aggregate boundaries, and solve complex domain problems through elegant architectural patterns.

## Introduction: From Anemic Services to Rich Workflows

Most applications handle business operations through anemic service classes that orchestrate between repositories and domain objects. This approach creates several problems:

- **Business logic spreads across services** instead of being centralized
- **Complex workflows become hard to follow** and debug
- **Cross-aggregate consistency** becomes difficult to maintain
- **Testing requires mocking** complex service interactions
- **Business rules duplicate** across different entry points

Domain-Driven Design offers a better approach through **command-based architectures** that:
- **Centralize business operations** in command handlers
- **Generate events** that describe what happened
- **Enable policies** to maintain consistency across aggregates
- **Provide clear audit trails** of all business operations
- **Support complex workflows** through event choreography

## The CQRS Foundation: Commands vs Queries

**Command Query Responsibility Segregation (CQRS)** is a pattern that separates operations that change state (commands) from operations that read state (queries).

### Why CQRS Matters

**Traditional CRUD Approach:**
```python
class UserService:
    def create_user(self, data): ...     # Create
    def get_user(self, id): ...          # Read  
    def update_user(self, id, data): ... # Update
    def delete_user(self, id): ...       # Delete
```

**Problems:**
- Single model tries to serve both read and write needs
- Complex queries pollute the write model
- Write operations return data instead of focusing on state change
- Business operations don't map well to CRUD operations

**CQRS Approach:**
```python
# Write side - focused on state changes
class CommandHandler:
    def handle_register_account(self, cmd: RegisterAccount) -> List[Event]: ...
    def handle_follow_account(self, cmd: FollowAccount) -> List[Event]: ...
    def handle_block_account(self, cmd: BlockAccount) -> List[Event]: ...

# Read side - focused on queries  
class QueryHandler:
    def get_account_profile(self, id: AccountId) -> AccountProfile: ...
    def get_follow_stats(self, id: AccountId) -> FollowStats: ...
    def get_relationship_status(self, id1: AccountId, id2: AccountId) -> RelationshipInfo: ...
```

**Benefits:**
- Write models focus purely on business logic
- Read models optimize for query performance
- Different scalability strategies for reads vs writes
- Clear separation of concerns

## Commands: Expressing Intent

**Commands represent the intent to change system state.** They are:
- **Imperative**: Express what should happen (RegisterAccount, FollowUser)
- **Data containers**: Carry the information needed for the operation
- **Immutable**: Once created, they shouldn't change
- **Can fail**: Not all commands result in successful state changes

### Command Design Principles

```python
from dataclasses import dataclass
from typing import Protocol
from abc import ABC

class Command(ABC):
    """Base class for all commands"""
    pass

@dataclass(frozen=True)
class RegisterAccount(Command):
    """
    Command to register a new user account.
    
    Design principles:
    - Immutable (frozen=True)
    - Contains only essential data for the operation
    - Uses domain value objects, not primitives
    - Self-documenting through naming and types
    """
    email: Email
    username: Username

@dataclass(frozen=True)
class FollowAccount(Command):
    """Command to create a follow relationship"""
    follower_id: AccountId
    followee_id: AccountId

@dataclass(frozen=True)
class BlockAccount(Command):
    """Command to block another user"""
    blocker_id: AccountId
    blocked_id: AccountId

@dataclass(frozen=True)
class RemoveFollower(Command):
    """Command to remove a follow relationship"""
    follower_id: AccountId
    followee_id: AccountId
    reason: str = "user_requested"
```

### Command Validation

Commands should validate their structure but not business rules:

```python
@dataclass(frozen=True)
class FollowAccount(Command):
    follower_id: AccountId
    followee_id: AccountId
    
    def __post_init__(self) -> None:
        # Structural validation only
        if not self.follower_id:
            raise ValueError("follower_id is required")
        if not self.followee_id:
            raise ValueError("followee_id is required")
        # Note: We don't check if accounts exist here - that's business logic
```

## The 4-Step Command Handling Pattern

**Every command handler should follow this consistent pattern:**

1. **Validate**: Check business rules and preconditions
2. **Fetch**: Load required aggregate state from repositories
3. **Execute**: Call domain methods to change state
4. **Save**: Persist changes and return events

This pattern ensures consistency, testability, and clear audit trails.

### Example: RegisterAccount Handler

```python
from typing import List, Optional

class AccountCommandHandler:
    def __init__(self, account_repo: AccountRepository, event_bus: EventBus):
        self.accounts = account_repo
        self.event_bus = event_bus
    
    def handle_register_account(self, cmd: RegisterAccount) -> List[Event]:
        """
        Handle account registration following the 4-step pattern.
        
        Business rules:
        - Email must be unique across all accounts
        - Username must be unique across all accounts
        - Account gets a unique ID
        """
        
        # 1. VALIDATE: Check business preconditions
        if self.accounts.exists_with_email(cmd.email):
            return [AccountRegistrationFailed(
                email=cmd.email,
                username=cmd.username,
                reason="Email already registered"
            )]
        
        if self.accounts.exists_with_username(cmd.username):
            return [AccountRegistrationFailed(
                email=cmd.email,
                username=cmd.username,
                reason="Username already taken"
            )]
        
        # 2. FETCH: No existing state needed for registration
        
        # 3. EXECUTE: Create new aggregate
        account, registration_event = Account.register(cmd.email, cmd.username)
        
        # 4. SAVE: Persist changes
        self.accounts.save(account)
        
        return [registration_event]
```

### Example: FollowAccount Handler

```python
def handle_follow_account(self, cmd: FollowAccount) -> List[Event]:
    """
    Handle follow request with comprehensive business rule checking.
    
    Business rules:
    - Cannot follow yourself
    - Cannot follow if either party has blocked the other
    - Cannot follow non-existent accounts
    - Following is idempotent (no error if already following)
    """
    
    # 1. VALIDATE: Check command structure and basic business rules
    if cmd.follower_id == cmd.followee_id:
        return [FollowRejected(
            follower_id=cmd.follower_id,
            followee_id=cmd.followee_id,
            reason="Cannot follow yourself"
        )]
    
    # 2. FETCH: Load required aggregates
    follower = self.accounts.get_by_id(cmd.follower_id)
    followee = self.accounts.get_by_id(cmd.followee_id)
    
    if not follower:
        return [FollowRejected(
            follower_id=cmd.follower_id,
            followee_id=cmd.followee_id,
            reason="Follower account not found"
        )]
    
    if not followee:
        return [FollowRejected(
            follower_id=cmd.follower_id,
            followee_id=cmd.followee_id,
            reason="Followee account not found"
        )]
    
    if not follower.is_active or not followee.is_active:
        return [FollowRejected(
            follower_id=cmd.follower_id,
            followee_id=cmd.followee_id,
            reason="One or both accounts are inactive"
        )]
    
    # Check blocking relationships
    if follower.is_blocked(cmd.followee_id) or followee.is_blocked(cmd.follower_id):
        return [FollowRejected(
            follower_id=cmd.follower_id,
            followee_id=cmd.followee_id,
            reason="Blocked relationship prevents following"
        )]
    
    # Check if already following (idempotent operation)
    if self.follows.exists(cmd.follower_id, cmd.followee_id):
        return []  # No event needed for idempotent operation
    
    # 3. EXECUTE: Create the relationship
    relationship, follow_event = FollowRelationship.create(
        cmd.follower_id, 
        cmd.followee_id
    )
    
    # 4. SAVE: Persist changes
    self.follows.save_relationship(relationship)
    
    return [follow_event]
```

### Example: BlockAccount Handler

```python
def handle_block_account(self, cmd: BlockAccount) -> List[Event]:
    """
    Handle account blocking with automatic follow cleanup.
    
    Business rules:
    - Cannot block yourself
    - Blocking is idempotent
    - Blocking should trigger follow relationship cleanup (via policy)
    """
    
    # 1. VALIDATE: Basic business rules
    if cmd.blocker_id == cmd.blocked_id:
        return [BlockRejected(
            blocker_id=cmd.blocker_id,
            blocked_id=cmd.blocked_id,
            reason="Cannot block yourself"
        )]
    
    # 2. FETCH: Load blocker account
    blocker = self.accounts.get_by_id(cmd.blocker_id)
    blocked = self.accounts.get_by_id(cmd.blocked_id)
    
    if not blocker:
        return [BlockRejected(
            blocker_id=cmd.blocker_id,
            blocked_id=cmd.blocked_id,
            reason="Blocker account not found"
        )]
    
    if not blocked:
        return [BlockRejected(
            blocker_id=cmd.blocker_id,
            blocked_id=cmd.blocked_id,
            reason="Account to block not found"
        )]
    
    # 3. EXECUTE: Block the account
    block_event = blocker.block_account(cmd.blocked_id)
    
    # 4. SAVE: Persist changes
    self.accounts.save(blocker)
    
    return [block_event]
```

## Events: Recording What Happened

**Events are immutable facts about what happened in the system.** They:
- **Use past tense**: AccountRegistered, UserFollowed, AccountBlocked
- **Are immutable**: Once published, they never change
- **Contain all relevant data**: Everything needed to understand what happened
- **Have timestamps**: When did this occur?
- **Are version-friendly**: Can evolve over time

### Event Design Patterns

```python
from datetime import datetime
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountRegistered(Event):
    """Published when a new account is successfully registered"""
    account_id: AccountId
    email: Email
    username: Username
    registered_at: datetime
    version: int = 1  # For event evolution

@dataclass(frozen=True)
class FollowCreated(Event):
    """Published when a follow relationship is created"""
    relationship_id: FollowRelationshipId
    follower_id: AccountId
    followee_id: AccountId
    created_at: datetime
    version: int = 1

@dataclass(frozen=True)
class AccountBlocked(Event):
    """Published when one account blocks another"""
    blocker_id: AccountId
    blocked_id: AccountId
    blocked_at: datetime
    was_already_blocked: bool  # For idempotency tracking
    version: int = 1

@dataclass(frozen=True)
class FollowRemoved(Event):
    """Published when a follow relationship is removed"""
    relationship_id: Optional[FollowRelationshipId]  # Might not exist
    follower_id: AccountId
    followee_id: AccountId
    removed_at: datetime
    reason: str  # "user_requested", "policy_triggered", "account_blocked"
    version: int = 1

# Failure events are also important
@dataclass(frozen=True)
class FollowRejected(Event):
    """Published when a follow attempt is rejected"""
    follower_id: AccountId
    followee_id: AccountId
    reason: str
    attempted_at: datetime = field(default_factory=datetime.now)
    version: int = 1
```

### Event Evolution

Events need to evolve over time. Design for it:

```python
@dataclass(frozen=True)
class AccountRegistered(Event):
    """Account registration event - version 2"""
    account_id: AccountId
    email: Email
    username: Username
    registered_at: datetime
    registration_source: str = "web"  # New field in v2
    marketing_consent: bool = False   # New field in v2
    version: int = 2

    @classmethod
    def from_v1(cls, v1_event: dict) -> 'AccountRegistered':
        """Convert from version 1 event"""
        return cls(
            account_id=AccountId(v1_event['account_id']),
            email=Email(v1_event['email']),
            username=Username(v1_event['username']),
            registered_at=v1_event['registered_at'],
            registration_source="web",  # Default for v1 events
            marketing_consent=False,    # Default for v1 events
            version=2
        )
```

## Event Bus: Connecting Components

The Event Bus enables **loose coupling** between components through **publish-subscribe** patterns:

```python
from typing import Dict, List, Callable, Type
from collections import defaultdict

EventHandler = Callable[[Event], None]

class EventBus:
    """
    Simple event bus for publishing and subscribing to domain events.
    
    Enables loose coupling between aggregates and cross-cutting concerns.
    """
    
    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[EventHandler]] = defaultdict(list)
        self._published_events: List[Event] = []  # For testing/debugging
    
    def subscribe(self, event_type: Type[Event], handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type"""
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all registered handlers.
        
        Handlers are called synchronously in registration order.
        For production, consider async handling and error isolation.
        """
        self._published_events.append(event)
        
        # Call all handlers for this event type
        for handler in self._subscribers.get(type(event), []):
            try:
                handler(event)
            except Exception as e:
                # In production, you'd want more sophisticated error handling
                print(f"Error in event handler: {e}")
                # Consider: logging, retries, dead letter queues
    
    def get_published_events(self) -> List[Event]:
        """Get all published events (useful for testing)"""
        return self._published_events.copy()
    
    def clear_published_events(self) -> None:
        """Clear published events (useful for testing)"""
        self._published_events.clear()
```

## Policies: Cross-Aggregate Business Rules

**Policies implement business rules that span multiple aggregates.** They:
- **Listen to events** from one aggregate
- **Issue commands** to other aggregates  
- **Maintain consistency** across aggregate boundaries
- **Implement complex business workflows**

### The Blocking Policy: Solving Our Core Problem

Remember our core problem from Part 1? When someone blocks another user, the follow relationship should be automatically removed. This is a **cross-aggregate policy**:

```python
class BlockingPolicy:
    """
    Implements business policy: When user A blocks user B, 
    remove any follow relationships between them.
    
    This solves the classic social media bug where blocked users
    remain visible due to persistent follow relationships.
    """
    
    def __init__(self, command_handler: 'ApplicationService'):
        self.command_handler = command_handler
    
    def handle_account_blocked(self, event: AccountBlocked) -> None:
        """
        React to account blocking by cleaning up follow relationships.
        
        Business rules implemented:
        1. If A blocks B, remove A->B follow relationship
        2. If A blocks B, remove B->A follow relationship  
        3. Operations are idempotent (safe if relationships don't exist)
        """
        blocker_id = event.blocker_id
        blocked_id = event.blocked_id
        
        # Remove follow relationship in both directions
        # This ensures blocked users cannot see each other's content
        
        # Remove blocked user following blocker
        self.command_handler.handle(RemoveFollower(
            follower_id=blocked_id,
            followee_id=blocker_id,
            reason="blocked_by_followee"
        ))
        
        # Remove blocker following blocked user
        self.command_handler.handle(RemoveFollower(
            follower_id=blocker_id,
            followee_id=blocked_id,
            reason="blocked_followee"
        ))
```

### Advanced Policy: Follow Limit Enforcement

```python
class FollowLimitPolicy:
    """
    Enforce business rule: Users cannot follow more than 5000 accounts.
    
    This prevents spam and ensures good user experience.
    """
    
    def __init__(self, follow_repo: FollowRepository, command_handler: 'ApplicationService'):
        self.follows = follow_repo
        self.command_handler = command_handler
    
    def handle_follow_created(self, event: FollowCreated) -> None:
        """Check if follow count exceeds limit"""
        follower_id = event.follower_id
        current_count = self.follows.count_following(follower_id)
        
        if current_count > 5000:
            # Remove the most recent follow (this one)
            self.command_handler.handle(RemoveFollower(
                follower_id=follower_id,
                followee_id=event.followee_id,
                reason="follow_limit_exceeded"
            ))
            
            # Could also publish an event for notification
            # self.event_bus.publish(FollowLimitExceeded(follower_id, current_count))
```

### Policy Registration

```python
class PolicyRegistry:
    """Central registry for all domain policies"""
    
    def __init__(self, event_bus: EventBus, command_handler: 'ApplicationService'):
        self.event_bus = event_bus
        self.command_handler = command_handler
        self._register_policies()
    
    def _register_policies(self) -> None:
        """Register all domain policies with the event bus"""
        
        # Blocking policy - removes follows when accounts are blocked
        blocking_policy = BlockingPolicy(self.command_handler)
        self.event_bus.subscribe(AccountBlocked, blocking_policy.handle_account_blocked)
        
        # Follow limit policy - enforces maximum follows per user
        follow_limit_policy = FollowLimitPolicy(
            self.command_handler.follows, 
            self.command_handler
        )
        self.event_bus.subscribe(FollowCreated, follow_limit_policy.handle_follow_created)
        
        # Account cleanup policy - removes all relationships when account is deleted
        cleanup_policy = AccountCleanupPolicy(self.command_handler)
        self.event_bus.subscribe(AccountDeactivated, cleanup_policy.handle_account_deactivated)
```

## Application Service: Orchestrating Everything

The Application Service coordinates commands, handlers, events, and policies:

```python
class SocialMediaApplication:
    """
    Main application service that orchestrates all business operations.
    
    Responsibilities:
    - Route commands to appropriate handlers
    - Publish events to event bus
    - Coordinate between aggregates
    - Manage transaction boundaries
    """
    
    def __init__(self, account_repo: AccountRepository, follow_repo: FollowRepository):
        self.accounts = account_repo
        self.follows = follow_repo
        self.event_bus = EventBus()
        
        # Register policies
        self.policy_registry = PolicyRegistry(self.event_bus, self)
        
        # Command routing
        self._command_handlers = {
            RegisterAccount: self._handle_register_account,
            FollowAccount: self._handle_follow_account,
            BlockAccount: self._handle_block_account,
            RemoveFollower: self._handle_remove_follower,
        }
    
    def handle(self, command: Command) -> List[Event]:
        """
        Main entry point for all business operations.
        
        Pattern:
        1. Route command to appropriate handler
        2. Execute business logic
        3. Publish resulting events
        4. Return events for caller inspection
        """
        handler = self._command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        
        # Execute business logic
        events = handler(command)
        
        # Publish events (triggers policies)
        for event in events:
            self.event_bus.publish(event)
        
        return events
    
    def _handle_register_account(self, cmd: RegisterAccount) -> List[Event]:
        """Implementation from earlier examples"""
        # ... (implementation shown earlier)
        pass
    
    def _handle_follow_account(self, cmd: FollowAccount) -> List[Event]:
        """Implementation from earlier examples"""
        # ... (implementation shown earlier)
        pass
    
    def _handle_block_account(self, cmd: BlockAccount) -> List[Event]:
        """Implementation from earlier examples"""
        # ... (implementation shown earlier)
        pass
    
    def _handle_remove_follower(self, cmd: RemoveFollower) -> List[Event]:
        """Handle follow relationship removal"""
        
        # 1. VALIDATE: Basic checks
        if cmd.follower_id == cmd.followee_id:
            return []  # Nothing to remove
        
        # 2. FETCH: Check if relationship exists
        if not self.follows.exists(cmd.follower_id, cmd.followee_id):
            return []  # Idempotent - no error if doesn't exist
        
        # 3. EXECUTE: Remove the relationship
        was_removed = self.follows.remove_relationship(cmd.follower_id, cmd.followee_id)
        
        # 4. SAVE: Already persisted by repository
        
        if was_removed:
            return [FollowRemoved(
                relationship_id=None,  # We don't track relationship IDs in this simple version
                follower_id=cmd.follower_id,
                followee_id=cmd.followee_id,
                removed_at=datetime.now(),
                reason=cmd.reason
            )]
        
        return []
```

## Testing Command Handlers and Policies

### Testing Command Handlers

```python
import pytest
from datetime import datetime

class TestAccountCommandHandler:
    def setup_method(self):
        """Set up fresh repositories for each test"""
        self.account_repo = InMemoryAccountRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.event_bus = EventBus()
        self.app = SocialMediaApplication(self.account_repo, self.follow_repo)
    
    def test_register_account_success(self):
        """Test successful account registration"""
        cmd = RegisterAccount(
            email=Email("test@example.com"),
            username=Username("testuser")
        )
        
        events = self.app.handle(cmd)
        
        # Verify event published
        assert len(events) == 1
        assert isinstance(events[0], AccountRegistered)
        assert events[0].email.value == "test@example.com"
        assert events[0].username.value == "testuser"
        
        # Verify account saved
        account = self.account_repo.get_by_email(Email("test@example.com"))
        assert account is not None
        assert account.username.value == "testuser"
    
    def test_register_account_duplicate_email(self):
        """Test registration with duplicate email"""
        email = Email("duplicate@example.com")
        
        # Register first account
        self.app.handle(RegisterAccount(email, Username("user1")))
        
        # Try to register second account with same email
        events = self.app.handle(RegisterAccount(email, Username("user2")))
        
        # Should get failure event
        assert len(events) == 1
        assert isinstance(events[0], AccountRegistrationFailed)
        assert "Email already registered" in events[0].reason
    
    def test_follow_account_success(self):
        """Test successful follow relationship creation"""
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
        
        # Verify event published
        assert len(follow_events) == 1
        assert isinstance(follow_events[0], FollowCreated)
        assert follow_events[0].follower_id == alice_id
        assert follow_events[0].followee_id == bob_id
        
        # Verify relationship exists
        assert self.follow_repo.exists(alice_id, bob_id)
    
    def test_follow_self_rejection(self):
        """Test that users cannot follow themselves"""
        # Create account
        events = self.app.handle(RegisterAccount(
            Email("alice@example.com"), Username("alice")
        ))
        alice_id = events[0].account_id
        
        # Try to follow self
        follow_events = self.app.handle(FollowAccount(alice_id, alice_id))
        
        # Should get rejection event
        assert len(follow_events) == 1
        assert isinstance(follow_events[0], FollowRejected)
        assert "Cannot follow yourself" in follow_events[0].reason
```

### Testing Policies

```python
class TestBlockingPolicy:
    def setup_method(self):
        """Set up application with policy"""
        self.account_repo = InMemoryAccountRepository()
        self.follow_repo = InMemoryFollowRepository()
        self.app = SocialMediaApplication(self.account_repo, self.follow_repo)
    
    def test_blocking_removes_follow_relationships(self):
        """Test that blocking automatically removes follow relationships"""
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
        self.app.handle(FollowAccount(alice_id, bob_id))
        assert self.follow_repo.exists(alice_id, bob_id)
        
        # Bob follows Alice
        self.app.handle(FollowAccount(bob_id, alice_id))
        assert self.follow_repo.exists(bob_id, alice_id)
        
        # Bob blocks Alice
        block_events = self.app.handle(BlockAccount(bob_id, alice_id))
        
        # Verify blocking event
        assert any(isinstance(e, AccountBlocked) for e in block_events)
        
        # Verify follow relationships were removed by policy
        assert not self.follow_repo.exists(alice_id, bob_id)
        assert not self.follow_repo.exists(bob_id, alice_id)
        
        # Check events published by policy
        all_events = self.app.event_bus.get_published_events()
        follow_removed_events = [e for e in all_events if isinstance(e, FollowRemoved)]
        assert len(follow_removed_events) == 2  # Both directions removed
```

## Error Handling and Resilience

### Handling Command Failures

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class CommandSuccess:
    events: List[Event]

@dataclass(frozen=True)
class CommandFailure:
    error: str
    reason: str

CommandResult = Union[CommandSuccess, CommandFailure]

class ResilientApplicationService:
    """Application service with robust error handling"""
    
    def handle_with_result(self, command: Command) -> CommandResult:
        """Handle command with explicit error handling"""
        try:
            events = self.handle(command)
            return CommandSuccess(events)
        except ValueError as e:
            return CommandFailure(
                error="validation_error",
                reason=str(e)
            )
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error handling {type(command).__name__}: {e}")
            return CommandFailure(
                error="system_error",
                reason="An unexpected error occurred"
            )
```

### Policy Error Isolation

```python
class ResilientEventBus:
    """Event bus with error isolation for policies"""
    
    def publish(self, event: Event) -> None:
        """Publish with error isolation"""
        failed_handlers = []
        
        for handler in self._subscribers.get(type(event), []):
            try:
                handler(event)
            except Exception as e:
                failed_handlers.append((handler, e))
                # Log but don't stop other handlers
                logger.error(f"Policy handler failed: {e}")
        
        # Could implement retry logic, dead letter queues, etc.
        if failed_handlers:
            self._handle_policy_failures(event, failed_handlers)
```

## Performance Considerations

### Batch Operations

```python
class BatchCommandHandler:
    """Handle multiple commands efficiently"""
    
    def handle_batch(self, commands: List[Command]) -> List[Event]:
        """Process multiple commands in a single transaction"""
        all_events = []
        
        # Group commands by type for optimization
        command_groups = self._group_commands_by_type(commands)
        
        for command_type, command_list in command_groups.items():
            if command_type == FollowAccount:
                events = self._handle_batch_follows(command_list)
            else:
                # Fall back to individual handling
                for cmd in command_list:
                    events.extend(self.handle(cmd))
            
            all_events.extend(events)
        
        return all_events
```

### Async Event Processing

```python
import asyncio
from typing import Awaitable

class AsyncEventBus:
    """Event bus with asynchronous policy execution"""
    
    async def publish_async(self, event: Event) -> None:
        """Publish event with async policy execution"""
        handlers = self._subscribers.get(type(event), [])
        
        # Execute all handlers concurrently
        tasks = [self._safe_execute_handler(handler, event) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_execute_handler(self, handler: EventHandler, event: Event) -> None:
        """Execute handler with error isolation"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Async policy handler failed: {e}")
```

## Summary: Building Robust Business Workflows

Commands, Handlers, Events, and Policies work together to create maintainable business workflows:

🎯 **Commands express business intent** clearly and immutably
🎯 **The 4-step pattern ensures consistency** across all operations
🎯 **Events provide audit trails** and enable loose coupling
🎯 **Policies maintain consistency** across aggregate boundaries
🎯 **Event buses enable reactive architectures** that scale naturally

**Key Architectural Benefits:**
- **Clear separation of concerns**: Commands change state, queries read state
- **Testable business logic**: Each handler follows a predictable pattern
- **Audit trail**: Events record exactly what happened and when
- **Loose coupling**: Policies react to events without tight dependencies
- **Scalable workflows**: Complex business processes emerge from simple event interactions

In our social media platform, we've implemented:
- **Command handlers** that follow the 4-step pattern for consistency
- **Rich events** that capture all business-relevant information
- **Cross-aggregate policies** that solve the blocking/following bug elegantly
- **Coordinated workflows** through the Application Service
- **Comprehensive testing** that validates both happy paths and edge cases

This architecture provides the foundation for complex business workflows while maintaining clean separation of concerns and enabling confident evolution of business rules.

---

**Next:** [Part 5 - Queries, Read Models, Tests](/courses/05-queries-read-models-tests/) - Learn to build optimized read models, implement comprehensive testing strategies, and create production-ready DDD applications.
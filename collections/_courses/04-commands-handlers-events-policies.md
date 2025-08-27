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

# Commands, Handlers, Events, Policies

**Goal:** Enable change and enforce business rules using a consistent, repeatable pattern.

## The 4-Step Command Handling Pattern

Every command handler follows this exact pattern:

1. **Validate** command data
2. **Fetch state** from repositories  
3. **Derive event** from business rules
4. **Update state** and publish events

## Commands

Commands represent intent to change state:

```python
@dataclass(frozen=True)
class RegisterAccount(Command):
    email: Email
    username: Username

@dataclass(frozen=True)
class FollowAccount(Command):
    follower_id: AccountId
    followee_id: AccountId

@dataclass(frozen=True)
class BlockAccount(Command):
    blocker_id: AccountId
    blocked_id: AccountId
```

## Command Handlers

### Example: RegisterAccount Handler

```python
def _handle_register_account(self, cmd: RegisterAccount) -> List[Event]:
    # 1) Validate
    # (done by Value Objects)
    
    # 2) Fetch state
    if self.accounts.get_by_email(cmd.email) or self.accounts.get_by_username(cmd.username):
        return [AccountAlreadyExists(email=cmd.email, username=cmd.username, reason="Duplicate email or username")]
    
    # 3) Derive event
    acc = Account(id=AccountId.new(), email=cmd.email, username=cmd.username)
    evt = AccountRegistered(acc.id, acc.email, acc.username)
    
    # 4) Update state
    self.accounts.save(acc)
    return [evt]
```

### Example: FollowAccount Handler

```python
def _handle_follow_account(self, cmd: FollowAccount) -> List[Event]:
    # 1) Validate
    if cmd.follower_id == cmd.followee_id:
        return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Cannot follow self")]
    
    # 2) Fetch state
    follower = self.accounts.get(cmd.follower_id)
    followee = self.accounts.get(cmd.followee_id)
    if not follower or not followee:
        return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Unknown accounts")]
    
    # 3) Derive event according to rules
    blocked_either_way = cmd.followee_id in follower.blocked or cmd.follower_id in followee.blocked
    if blocked_either_way:
        return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Blocked relationship")]
    if self.follows.exists(cmd.follower_id, cmd.followee_id):
        return []  # idempotent
    
    # 4) Update state
    self.follows.add(cmd.follower_id, cmd.followee_id)
    return [AccountFollowed(cmd.follower_id, cmd.followee_id)]
```

## Event Bus

```python
class EventBus:
    def __init__(self) -> None:
        self.subscribers: Dict[Type[Event], List[PolicyFn]] = defaultdict(list)

    def subscribe(self, event_type: Type[Event], handler: PolicyFn) -> None:
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for fn in self.subscribers.get(type(event), []):
            fn(event)
```

## Policies: Event-Driven Glue

**Policies** are the secret to fixing our classic bug! They listen for events and issue commands:

```python
def _register_policies(self) -> None:
    # When B blocks A, remove A -> B follow link if present
    def on_account_blocked(ev: Event) -> None:
        assert isinstance(ev, AccountBlocked)
        follower = ev.blocked_id
        followee = ev.blocker_id
        self.handle(RemoveFollower(follower_id=follower, followee_id=followee))
    
    self.bus.subscribe(AccountBlocked, on_account_blocked)
```

This policy **automatically removes the follow relationship** when someone gets blocked, fixing our bug!

## Application Coordination

```python
class Application:
    def handle(self, cmd: Command) -> List[Event]:
        handler = self.handlers.get(type(cmd))
        if not handler:
            raise ValueError(f"No handler for {type(cmd).__name__}")
        events = handler(cmd)
        for ev in events:
            self.bus.publish(ev)  # Triggers policies!
        return events
```

## The Bug Fix in Action

1. **Alice follows Bob** → `AccountFollowed` event
2. **Bob blocks Alice** → `AccountBlocked` event  
3. **Policy triggers** → Issues `RemoveFollower` command
4. **Follow removed** → `FollowerRemoved` event
5. **Bug fixed!** ✅

## Exercises

### Add Business Rules
* Add a rule: if you block someone, you also stop following them. Encode that as an extra `RemoveFollower` in the policy.
* Add an idempotency check in `BlockAccount` so repeated blocks do not churn events.

### Three-Step Improvement

**Immediate patch:** Enforce the 4 steps in every handler.

**Deeper cause:** Mixing application coordination and domain decisions.

**Optional improvement:** Use an explicit DomainEvent list returned by aggregates to keep mutation in one place.

## Key Insights

🎯 **The 4-step pattern is your friend** - validate, fetch, derive, update
🎯 **Policies handle cross-aggregate concerns** - keep them in the event bus layer  
🎯 **Events are facts** - they describe what happened in past tense
🎯 **Commands are intent** - they describe what should happen

---

**Next:** [Part 5 - Queries, Read Models, Tests](/courses/05-queries-read-models-tests/) - Learn to keep reads simple and build fit-for-purpose read models.
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Dict, List, Callable, Type, DefaultDict, Optional, Iterable, Tuple
from collections import defaultdict
import re
import uuid

# -------- Value Objects --------

@dataclass(frozen=True)
class AccountId:
    value: str

    @staticmethod
    def new() -> "AccountId":
        return AccountId(str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


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


# -------- Domain Events --------

class Event:  # marker
    pass

@dataclass(frozen=True)
class AccountRegistered(Event):
    account_id: AccountId
    email: Email
    username: Username

@dataclass(frozen=True)
class AccountAlreadyExists(Event):
    email: Email | None
    username: Username | None
    reason: str

@dataclass(frozen=True)
class AccountFollowed(Event):
    follower_id: AccountId
    followee_id: AccountId

@dataclass(frozen=True)
class FollowRejectedBlocked(Event):
    follower_id: AccountId
    followee_id: AccountId
    reason: str

@dataclass(frozen=True)
class AccountBlocked(Event):
    blocker_id: AccountId
    blocked_id: AccountId

@dataclass(frozen=True)
class FollowerRemoved(Event):
    follower_id: AccountId
    followee_id: AccountId
    reason: str


# -------- Commands --------

class Command:  # marker
    pass

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

@dataclass(frozen=True)
class RemoveFollower(Command):
    follower_id: AccountId
    followee_id: AccountId


# -------- Entities and Aggregates --------

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


# -------- Repositories --------

class AccountRepository(Protocol):
    def get(self, account_id: AccountId) -> Optional[Account]: ...
    def get_by_email(self, email: Email) -> Optional[Account]: ...
    def get_by_username(self, username: Username) -> Optional[Account]: ...
    def save(self, account: Account) -> None: ...

class FollowRepository(Protocol):
    def exists(self, follower: AccountId, followee: AccountId) -> bool: ...
    def add(self, follower: AccountId, followee: AccountId) -> None: ...
    def remove(self, follower: AccountId, followee: AccountId) -> None: ...
    def followers_of(self, account: AccountId) -> List[AccountId]: ...
    def following_of(self, account: AccountId) -> List[AccountId]: ...

# In memory implementations suitable for workshop use

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

    def get_by_username(self, username: Username) -> Optional[Account]:
        aid = self.by_username.get(username.value)
        return self.by_id.get(aid) if aid else None

    def save(self, account: Account) -> None:
        self.by_id[account.id.value] = account
        self.by_email[account.email.value] = account.id.value
        self.by_username[account.username.value] = account.id.value


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

    def remove(self, follower: AccountId, followee: AccountId) -> None:
        self.following[follower.value].discard(followee.value)
        self.followers[followee.value].discard(follower.value)

    def followers_of(self, account: AccountId) -> List[AccountId]:
        return [AccountId(fid) for fid in sorted(self.followers[account.value])]

    def following_of(self, account: AccountId) -> List[AccountId]:
        return [AccountId(fid) for fid in sorted(self.following[account.value])]


# -------- Event Bus and Application Shell --------

HandlerFn = Callable[[Command], List[Event]]
PolicyFn = Callable[[Event], None]

class EventBus:
    def __init__(self) -> None:
        self.subscribers: Dict[Type[Event], List[PolicyFn]] = defaultdict(list)

    def subscribe(self, event_type: Type[Event], handler: PolicyFn) -> None:
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for fn in self.subscribers.get(type(event), []):
            fn(event)


class Application:
    def __init__(self, accounts: AccountRepository, follows: FollowRepository) -> None:
        self.accounts = accounts
        self.follows = follows
        self.bus = EventBus()
        self.handlers: Dict[Type[Command], HandlerFn] = {}
        self._register_handlers()
        self._register_policies()

        # simple read model
        self.read_followers: DefaultDict[str, set[str]] = defaultdict(set)
        self.read_following: DefaultDict[str, set[str]] = defaultdict(set)
        self.bus.subscribe(AccountRegistered, self._project)
        self.bus.subscribe(AccountFollowed, self._project)
        self.bus.subscribe(FollowerRemoved, self._project)

    # ---- Command handling entry point ----
    def handle(self, cmd: Command) -> List[Event]:
        handler = self.handlers.get(type(cmd))
        if not handler:
            raise ValueError(f"No handler for {type(cmd).__name__}")
        events = handler(cmd)
        for ev in events:
            self.bus.publish(ev)
        return events

    # ---- Handlers ----
    def _register_handlers(self) -> None:
        self.handlers[RegisterAccount] = self._handle_register_account
        self.handlers[FollowAccount] = self._handle_follow_account
        self.handlers[BlockAccount] = self._handle_block_account
        self.handlers[RemoveFollower] = self._handle_remove_follower

    # 4 step pattern in each handler

    def _handle_register_account(self, cmd: RegisterAccount) -> List[Event]:
        # 1) validate
        # done by Value Objects
        # 2) fetch state
        if self.accounts.get_by_email(cmd.email) or self.accounts.get_by_username(cmd.username):
            return [AccountAlreadyExists(email=cmd.email, username=cmd.username, reason="Duplicate email or username")]
        # 3) derive event
        acc = Account(id=AccountId.new(), email=cmd.email, username=cmd.username)
        evt = AccountRegistered(acc.id, acc.email, acc.username)
        # 4) update state
        self.accounts.save(acc)
        return [evt]

    def _handle_follow_account(self, cmd: FollowAccount) -> List[Event]:
        # 1) validate
        if cmd.follower_id == cmd.followee_id:
            return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Cannot follow self")]
        # 2) fetch state
        follower = self.accounts.get(cmd.follower_id)
        followee = self.accounts.get(cmd.followee_id)
        if not follower or not followee:
            return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Unknown accounts")]
        # 3) derive event according to rules
        blocked_either_way = cmd.followee_id in follower.blocked or cmd.follower_id in followee.blocked
        if blocked_either_way:
            return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Blocked relationship")]
        if self.follows.exists(cmd.follower_id, cmd.followee_id):
            return []  # idempotent
        # 4) update state
        self.follows.add(cmd.follower_id, cmd.followee_id)
        return [AccountFollowed(cmd.follower_id, cmd.followee_id)]

    def _handle_block_account(self, cmd: BlockAccount) -> List[Event]:
        # 1) validate
        if cmd.blocker_id == cmd.blocked_id:
            # no-op
            return []
        # 2) fetch state
        blocker = self.accounts.get(cmd.blocker_id)
        blocked = self.accounts.get(cmd.blocked_id)
        if not blocker or not blocked:
            return []
        # 3) derive event
        evt = blocker.block(cmd.blocked_id)  # returns AccountBlocked
        # 4) update state
        self.accounts.save(blocker)
        return [evt]

    def _handle_remove_follower(self, cmd: RemoveFollower) -> List[Event]:
        # 1) validate: nothing complex
        # 2) fetch state
        if not self.follows.exists(cmd.follower_id, cmd.followee_id):
            return []  # idempotent
        # 3) derive event
        evt = FollowerRemoved(cmd.follower_id, cmd.followee_id, reason="Blocked")
        # 4) update state
        self.follows.remove(cmd.follower_id, cmd.followee_id)
        return [evt]

    # ---- Policies ----
    def _register_policies(self) -> None:
        # When B blocks A, remove A -> B follow link if present
        def on_account_blocked(ev: Event) -> None:
            assert isinstance(ev, AccountBlocked)
            follower = ev.blocked_id
            followee = ev.blocker_id
            self.handle(RemoveFollower(follower_id=follower, followee_id=followee))
        self.bus.subscribe(AccountBlocked, on_account_blocked)

    # ---- Read model projector ----
    def _project(self, ev: Event) -> None:
        if isinstance(ev, AccountRegistered):
            # nothing to project for follows
            return
        if isinstance(ev, AccountFollowed):
            self.read_following[ev.follower_id.value].add(ev.followee_id.value)
            self.read_followers[ev.followee_id.value].add(ev.follower_id.value)
        if isinstance(ev, FollowerRemoved):
            self.read_following[ev.follower_id.value].discard(ev.followee_id.value)
            self.read_followers[ev.followee_id.value].discard(ev.follower_id.value)


# -------- Demo scenario for the workshop --------

def demo() -> None:
    accounts = InMemoryAccountRepo()
    follows = InMemoryFollowRepo()
    app = Application(accounts, follows)

    # Register two users
    [ev1] = app.handle(RegisterAccount(Email("aexample.com"), Username("alice_uk")))
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

if __name__ == "__main__":
    demo()
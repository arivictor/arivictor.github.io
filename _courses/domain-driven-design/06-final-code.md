---
course: DDD 101
part: 6
title: "DDD 101 - Part 6: Final Code"
---

## Final Code

```python
import sqlite3, re, uuid
from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Type
from collections import defaultdict

# ============================================================
# Domain Layer
# ============================================================

# ---- Value Objects ----

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

# ---- Domain Events ----

class Event: pass

@dataclass(frozen=True)
class AccountRegistered(Event):
    account_id: AccountId
    email: Email
    username: Username

@dataclass(frozen=True)
class AccountAlreadyExists(Event):
    email: Email
    username: Username
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

# ---- Commands ----

class Command: pass

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

# ---- Aggregate ----

@dataclass
class Account:
    id: AccountId
    email: Email
    username: Username
    def register(self) -> List[Event]:
        return [AccountRegistered(self.id, self.email, self.username)]

# ============================================================
# Application Layer
# ============================================================

# ---- Event Bus ----

PolicyFn = Callable[[Event], None]
class EventBus:
    def __init__(self) -> None:
        self.subscribers: Dict[Type[Event], List[PolicyFn]] = defaultdict(list)
    def subscribe(self, event_type: Type[Event], handler: PolicyFn) -> None:
        self.subscribers[event_type].append(handler)
    def publish(self, event: Event) -> None:
        for fn in self.subscribers.get(type(event), []):
            fn(event)

# ---- Command Handlers ----

class RegisterAccountHandler:
    def __init__(self, repo, bus): self.repo, self.bus = repo, bus
    def handle(self, cmd: RegisterAccount) -> List[Event]:
        if self.repo.get_by_email(cmd.email) or self.repo.get_by_username(cmd.username):
            return [AccountAlreadyExists(cmd.email, cmd.username, "Duplicate")]
        acc = Account(AccountId.new(), cmd.email, cmd.username)
        self.repo.save_account(acc)
        events = acc.register()
        for ev in events: self.bus.publish(ev)
        return events

class FollowAccountHandler:
    def __init__(self, repo, bus): self.repo, self.bus = repo, bus
    def handle(self, cmd: FollowAccount) -> List[Event]:
        f, t = self.repo.get(cmd.follower_id), self.repo.get(cmd.followee_id)
        if not f or not t:
            return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Unknown accounts")]
        if self.repo.is_blocked(cmd.follower_id, cmd.followee_id):
            return [FollowRejectedBlocked(cmd.follower_id, cmd.followee_id, "Blocked")]
        if self.repo.follows(cmd.follower_id, cmd.followee_id):
            return []
        self.repo.add_follow(cmd.follower_id, cmd.followee_id)
        ev = AccountFollowed(cmd.follower_id, cmd.followee_id)
        self.bus.publish(ev)
        return [ev]

class BlockAccountHandler:
    def __init__(self, repo, bus): self.repo, self.bus = repo, bus
    def handle(self, cmd: BlockAccount) -> List[Event]:
        if not self.repo.get(cmd.blocker_id) or not self.repo.get(cmd.blocked_id):
            return []
        self.repo.add_block(cmd.blocker_id, cmd.blocked_id)
        ev = AccountBlocked(cmd.blocker_id, cmd.blocked_id)
        self.bus.publish(ev)
        return [ev]

class RemoveFollowerHandler:
    def __init__(self, repo, bus): self.repo, self.bus = repo, bus
    def handle(self, cmd: RemoveFollower) -> List[Event]:
        if not self.repo.follows(cmd.follower_id, cmd.followee_id):
            return []
        self.repo.remove_follow(cmd.follower_id, cmd.followee_id)
        ev = FollowerRemoved(cmd.follower_id, cmd.followee_id, "Blocked")
        self.bus.publish(ev)
        return [ev]

# ---- Policies ----

class RemoveFollowerOnBlockPolicy:
    def __init__(self, app): self.app = app
    def handle(self, ev: AccountBlocked) -> None:
        self.app.remove_follower(RemoveFollower(ev.blocked_id, ev.blocker_id))

# ---- Application Facade (thin) ----

class ApplicationServices:
    def __init__(self, repo):
        self.repo = repo
        self.bus = EventBus()
        self.register_account = RegisterAccountHandler(repo, self.bus).handle
        self.follow_account = FollowAccountHandler(repo, self.bus).handle
        self.block_account = BlockAccountHandler(repo, self.bus).handle
        self.remove_follower = RemoveFollowerHandler(repo, self.bus).handle
        # policies
        self.bus.subscribe(AccountBlocked, RemoveFollowerOnBlockPolicy(self).handle)

# ============================================================
# Infrastructure Layer
# ============================================================

class SQLiteAccountRepo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn; self._init_schema()
    def _init_schema(self) -> None:
        c=self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY,email TEXT UNIQUE,username TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS follows(follower TEXT,followee TEXT,UNIQUE(follower,followee))")
        c.execute("CREATE TABLE IF NOT EXISTS blocks(blocker TEXT,blocked TEXT,UNIQUE(blocker,blocked))")
        self.conn.commit()
    def get(self, aid: AccountId) -> Optional[Account]:
        c=self.conn.cursor();c.execute("SELECT id,email,username FROM accounts WHERE id=?",(aid.value,))
        r=c.fetchone(); 
        return Account(AccountId(r[0]),Email(r[1]),Username(r[2])) if r else None

    def get_by_email(self,email:Email)->Optional[Account]:
        c=self.conn.cursor();c.execute("SELECT id FROM accounts WHERE email=?",(email.value,))
        r=c.fetchone(); return self.get(AccountId(r[0])) if r else None

    def get_by_username(self,u:Username)->Optional[Account]:
        c=self.conn.cursor();c.execute("SELECT id FROM accounts WHERE username=?",(u.value,))
        r=c.fetchone(); return self.get(AccountId(r[0])) if r else None

    def save_account(self,acc:Account)->None:
        self.conn.execute("INSERT OR IGNORE INTO accounts(id,email,username) VALUES(?,?,?)",
                          (acc.id.value,acc.email.value,acc.username.value)); self.conn.commit()

    def add_follow(self,f:AccountId,t:AccountId)->None:
        self.conn.execute("INSERT OR IGNORE INTO follows VALUES(?,?)",(f.value,t.value)); self.conn.commit()

    def remove_follow(self,f:AccountId,t:AccountId)->None:
        self.conn.execute("DELETE FROM follows WHERE follower=? AND followee=?",(f.value,t.value)); self.conn.commit()

    def add_block(self,b:AccountId,x:AccountId)->None:
        self.conn.execute("INSERT OR IGNORE INTO blocks VALUES(?,?)",(b.value,x.value)); self.conn.commit()
    
    def is_blocked(self,a:AccountId,b:AccountId)->bool:
        c=self.conn.cursor();c.execute("SELECT 1 FROM blocks WHERE(blocker=?AND blocked=?)OR(blocker=?AND blocked=?)",(a.value,b.value,b.value,a.value)); return c.fetchone()is not None
    
    def follows(self,f:AccountId,t:AccountId)->bool:
        c=self.conn.cursor();c.execute("SELECT 1 FROM follows WHERE follower=? AND followee=?",(f.value,t.value))
        return c.fetchone()is not None

    def get_following(self,a:AccountId)->List[AccountId]:
        c=self.conn.cursor();c.execute("SELECT followee FROM follows WHERE follower=?",(a.value,))
        return [AccountId(r[0]) for r in c.fetchall()]

# ============================================================
# Interface Layer (demo CLI)
# ============================================================

def demo():
    conn = sqlite3.connect(":memory:")
    repo = SQLiteAccountRepo(conn)
    app = ApplicationServices(repo)

    e1 = app.register_account(RegisterAccount(Email("a@example.com"), Username("alice")))[0]
    e2 = app.register_account(RegisterAccount(Email("b@example.com"), Username("bob")))[0]
    a, b = e1.account_id, e2.account_id

    app.follow_account(FollowAccount(a, b))
    print("Before block:", repo.get_following(a))

    app.block_account(BlockAccount(b, a))
    print("After block:", repo.get_following(a))

if __name__ == "__main__":
    demo()
```
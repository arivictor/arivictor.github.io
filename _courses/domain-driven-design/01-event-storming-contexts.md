---
course: DDD 101
part: 1
title: "DDD 101 - Part 1: Event Storming and Contexts"
date: 2025-08-27
---

# Event Storming and Bounded Contexts

**Goal:** Discover the domain language, the important events, where things can fail, and how to slice the system into manageable bounded contexts.

## Introduction: Why Event Storming?

Most software projects fail not because of technical complexity, but because teams build the wrong thing or build the right thing in the wrong way. Traditional requirements gathering often produces static documents that miss the dynamic nature of business processes. Event Storming, invented by Alberto Brandolini, flips this approach on its head.

**Event Storming is a collaborative workshop technique that:**
- **Reveals the real business process** through the events that matter to domain experts
- **Uncovers hidden complexities** that traditional analysis misses
- **Creates a shared mental model** between business and technical teams
- **Identifies natural boundaries** for system decomposition

Think of events as the heartbeat of your business. Every meaningful thing that happens in your domain can be expressed as an event in the past tense: `OrderPlaced`, `PaymentProcessed`, `CustomerRegistered`. By focusing on these events first, we discover what actually matters to the business.

## The Psychology Behind Event Storming

Why does Event Storming work so well? It leverages several psychological principles:

1. **Narrative Thinking**: Humans naturally think in stories. Events tell the story of your business.
2. **Visual Learning**: The colorful sticky notes and spatial arrangement engage different parts of the brain.
3. **Collaborative Discovery**: Multiple perspectives reveal blind spots that individual analysis misses.
4. **Temporal Sequencing**: Events naturally expose cause-and-effect relationships.

## Domain-Driven Design Context

Event Storming is a key practice in Domain-Driven Design (DDD), a strategic approach to software development that:

- **Places the domain at the center** of software design decisions
- **Uses the ubiquitous language** - a common vocabulary shared by business and technical teams
- **Identifies bounded contexts** - autonomous boundaries where specific models are valid
- **Focuses on core complexity** rather than technical accidental complexity

The goal isn't just to capture requirements, but to develop a deep understanding of the business that drives architectural decisions.

## Our Practice Domain: Social Media Platform

We'll explore DDD concepts through a social media platform that seems simple on the surface but reveals interesting complexity:

**Core Features:**
- Users register accounts with email and username
- Users can follow other users to see their content
- Users can block other users to prevent interactions
- Users can unfollow or be removed from follower lists

**The Hidden Complexity:**
This seemingly simple domain contains a classic bug that many social media platforms have struggled with: **What happens when user A follows user B, then B blocks A?** 

In many systems, A continues to see B's content because the follow relationship persists even after blocking. This violates user expectations and can enable harassment. We'll use DDD patterns to solve this elegantly.

## Event Storming Process

### Step 1: Domain Events Discovery

**Domain Events represent facts that have happened in the past.** They are:
- **Immutable**: Once they've happened, they can't be changed
- **Significant**: They matter to at least one domain expert
- **Past tense**: Use verbs in past tense (AccountRegistered, not RegisterAccount)

**Start with the happy path:**

```
UserRegistered → UserFollowed → ContentPosted → ContentViewed
```

**Then add the complexity:**

```
UserBlocked → FollowerRemoved → ContentHidden
```

**Color coding:**
- 🟠 **Orange**: Domain events (what happened)
- 🟦 **Blue**: Commands (what user intends)
- 🟥 **Red**: Failure events (what went wrong)
- 🟡 **Yellow**: Actors (who triggered it)
- 🟢 **Green**: External systems (what's outside our control)

### Step 2: Commands and Actors

**Commands represent intent to change state.** They:
- **Use imperative mood**: RegisterAccount, FollowUser, BlockUser
- **Can fail**: Not all commands result in successful events
- **Originate from actors**: Users, admins, systems, or time

```python
# Example command-to-event flow
RegisterAccount → UserRegistered | RegistrationFailed
FollowUser → UserFollowed | FollowRejected
BlockUser → UserBlocked | BlockingFailed
```

**Actors in our domain:**
- 👤 **End User**: Primary actor performing social actions
- 👮 **Moderator**: Admin user with special privileges
- 🤖 **System**: Automated processes (cleanup, notifications)
- ⏰ **Time**: Time-based triggers (subscription expiry)

### Step 3: Bounded Contexts Identification

**Bounded contexts are autonomous boundaries** where a specific domain model is valid. They help us:
- **Manage complexity** by dividing the problem space
- **Enable autonomous teams** to work independently  
- **Reduce coupling** between different parts of the system
- **Allow different models** for the same real-world concepts

**Our identified contexts:**

```
┌─────────────────┐    ┌──────────────────┐
│ Account Context │    │ Social Context   │
│                 │    │                  │
│ • Registration  │    │ • Following      │
│ • Authentication│◄──►│ • Blocking       │
│ • Profile Mgmt  │    │ • Relationships  │
│                 │    │                  │
└─────────────────┘    └──────────────────┘
```

**Context boundaries are revealed by:**
- **Different vocabularies**: "User" vs "Account" vs "Profile"
- **Different rules**: Account context cares about uniqueness, Social context cares about relationships
- **Different data ownership**: Who is the authoritative source?
- **Different change rates**: Authentication changes slowly, social features change frequently

## Deep Dive: Event Flow Analysis

Let's trace through our core business scenario to understand the event flow:

### Scenario: User Registration and Following

```python
# Initial registration
RegisterAccount(email="alice@example.com", username="alice")
  └─→ AccountRegistered(id="alice-123", email="alice@example.com", username="alice")

RegisterAccount(email="bob@example.com", username="bob")  
  └─→ AccountRegistered(id="bob-456", email="bob@example.com", username="bob")

# Alice follows Bob
FollowUser(follower="alice-123", followee="bob-456")
  └─→ UserFollowed(follower="alice-123", followee="bob-456")

# Bob blocks Alice (this should remove the follow!)
BlockUser(blocker="bob-456", blocked="alice-123")
  └─→ UserBlocked(blocker="bob-456", blocked="alice-123")
  └─→ FollowerRemoved(follower="alice-123", followee="bob-456")  # ← Policy-driven!
```

Notice how `UserBlocked` triggers `FollowerRemoved` - this is a **business policy** that will be implemented later as an event handler.

### Scenario: Edge Cases and Failures

```python
# Attempt to follow yourself
FollowUser(follower="alice-123", followee="alice-123")
  └─→ FollowRejected(follower="alice-123", followee="alice-123", reason="self-follow")

# Attempt to follow someone who blocked you
FollowUser(follower="alice-123", followee="bob-456")  # Bob already blocked Alice
  └─→ FollowRejected(follower="alice-123", followee="bob-456", reason="blocked")

# Double registration attempt
RegisterAccount(email="alice@example.com", username="alice2")
  └─→ RegistrationFailed(email="alice@example.com", reason="email-taken")
```

## Bounded Context Deep Dive

### Account Context

**Responsibilities:**
- User registration and authentication
- Profile management
- Account security (passwords, 2FA)
- Account status (active, suspended, deleted)

**Key Events:**
- `AccountRegistered`, `AccountActivated`, `AccountSuspended`
- `ProfileUpdated`, `PasswordChanged`
- `LoginAttempted`, `LoginSucceeded`, `LoginFailed`

**Ubiquitous Language:**
- **Account**: The system representation of a user
- **Profile**: Public information about an account
- **Credentials**: Authentication information

### Social Context

**Responsibilities:**
- Following relationships
- Blocking relationships  
- Feed generation (out of scope for now)
- Social recommendations

**Key Events:**
- `UserFollowed`, `UserUnfollowed`, `FollowerRemoved`
- `UserBlocked`, `UserUnblocked`
- `RelationshipStatusChanged`

**Ubiquitous Language:**
- **Follower**: Someone who follows another user
- **Followee**: Someone being followed
- **Relationship**: The connection between two users
- **Block**: Prevention of interaction between users

### Context Integration Patterns

**How contexts communicate:**

```
Account Context          Social Context
      │                        │
      ├─ AccountRegistered ────→│ (creates social profile)
      │                        │
      │                        ├─ UserBlocked
      │                        │     │
      │                        │     └─→ FollowerRemoved (policy)
      │                        │
      ├─ AccountDeleted ───────→│ (cleanup relationships)
```

**Integration strategies:**
- **Event notification**: Contexts publish events others can subscribe to
- **Shared kernel**: Common value objects (AccountId, Email)
- **Anti-corruption layer**: Translate between different models

## Common Event Storming Pitfalls

### 1. **Technology Focus Too Early**
❌ "We need a microservice for user management"
✅ "Users need to register and manage their accounts"

### 2. **CRUD Thinking**
❌ "CreateUser, UpdateUser, DeleteUser"  
✅ "UserRegistered, ProfileUpdated, AccountDeactivated"

### 3. **Missing the Verbs**
❌ "User, Account, Profile" (all nouns)
✅ "UserRegistered, AccountVerified, ProfileCompleted" (events as verbs)

### 4. **Too Much Technical Detail**
❌ "Save to database, send email, update cache"
✅ "UserRegistered, WelcomeEmailSent, ProfileIndexed"

### 5. **Skipping Failure Scenarios**
❌ Only modeling happy path
✅ Including RegistrationFailed, FollowRejected, etc.

## Best Practices for Event Storming

### 1. **Start with the End in Mind**
Begin with the business outcome: "User successfully follows another user and sees their content"

### 2. **Use Domain Expert Language**
If they say "friending," don't force "following." Capture their language first.

### 3. **Timebox Discovery Sessions**
- 2 hours maximum per session
- Take breaks every 45 minutes
- Schedule follow-up sessions rather than marathon workshops

### 4. **Invite the Right People**
- Domain experts who know the business rules
- Developers who will implement the system
- Product owners who understand user needs

### 5. **Focus on Events, Not Data**
Think "What happened?" not "What data do we store?"

## Implementation Preview: From Events to Code

Here's how our event storming discoveries translate to code structure:

```python
# Value Objects (shared between contexts)
@dataclass(frozen=True)
class AccountId:
    value: str

@dataclass(frozen=True) 
class Email:
    value: str

# Domain Events (from our event storming)
@dataclass(frozen=True)
class AccountRegistered:
    account_id: AccountId
    email: Email
    username: str
    timestamp: datetime

@dataclass(frozen=True)
class UserFollowed:
    follower_id: AccountId
    followee_id: AccountId
    timestamp: datetime

@dataclass(frozen=True)
class UserBlocked:
    blocker_id: AccountId
    blocked_id: AccountId
    timestamp: datetime

# Commands (from our event storming)
@dataclass
class RegisterAccount:
    email: Email
    username: str

@dataclass
class FollowUser:
    follower_id: AccountId
    followee_id: AccountId
```

## Context Mapping Exercise

**Map the relationships between your bounded contexts:**

```
    Account Context
         │
         │ AccountRegistered
         ▼
    Social Context ◄─── Content Context
         │                   │
         │ UserBlocked        │ PostCreated
         ▼                   ▼
   Notification Context ◄────┘
```

**Questions to ask:**
- Which context is the authoritative source for each concept?
- How do contexts communicate (events, APIs, shared database)?
- What happens when a context is temporarily unavailable?
- Which contexts can evolve independently?

## Real-World Context Examples

### E-commerce Platform
- **Catalog Context**: Product information, pricing, inventory
- **Shopping Context**: Cart, checkout, order placement  
- **Fulfillment Context**: Shipping, tracking, delivery
- **Payment Context**: Billing, payment processing, refunds

### Healthcare System
- **Patient Context**: Demographics, contact info, insurance
- **Clinical Context**: Diagnoses, treatments, medical history
- **Scheduling Context**: Appointments, resources, availability
- **Billing Context**: Claims, payments, insurance processing

## Hands-On Workshop Activity

### Setup (15 minutes)
1. **Gather materials**: Sticky notes (orange, blue, red, yellow, green), markers, large wall space
2. **Set the scene**: "We're building a social media platform. Users want to follow each other but also need protection from harassment."

### Discovery Phase (45 minutes)

**Round 1: Happy Path Events (15 minutes)**
- Start with user registration
- Follow the journey through following someone
- End with content consumption

**Round 2: Add Complexity (15 minutes)**  
- What happens when someone blocks another user?
- What about failed registration attempts?
- Add moderation scenarios

**Round 3: Context Boundaries (15 minutes)**
- Group related events together
- Draw boundaries around coherent clusters
- Name your bounded contexts

### Analysis Phase (30 minutes)

**Identify Patterns:**
- Which events frequently happen together?
- Which events are completely independent?
- Where do you see natural transaction boundaries?

**Question Everything:**
- Why does this event exist?
- Who cares about this event?
- What business rule does this event enforce or violate?

## Key Takeaways

🎯 **Events reveal the true business process** - not the idealized documentation version

🎯 **Bounded contexts emerge naturally** - don't force artificial boundaries

🎯 **Language matters** - use the words domain experts use

🎯 **Failures are first-class citizens** - model what goes wrong, not just what goes right

🎯 **Policies connect contexts** - events in one context can trigger actions in another

🎯 **Start simple, evolve complexity** - begin with the minimal viable model

## Summary

Event Storming gives us a collaborative technique to discover the real complexity in our domain. By focusing on events first, we naturally uncover:

- **The ubiquitous language** that business and technical teams can share
- **Bounded contexts** that help us decompose complex systems
- **Business policies** that connect different parts of the domain
- **Edge cases and failures** that requirements often miss

In our social media example, we discovered that user blocking isn't just about preventing future interactions - it also requires cleaning up existing relationships. This policy-driven approach will become the foundation for our implementation in the following parts.

The events and contexts we've identified provide the vocabulary and boundaries for building a robust, maintainable system that accurately reflects the business needs.
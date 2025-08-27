---
layout: course
title: "DDD Workshop Part 1: Event Storming and Contexts"
part: "Part 1 of 5"
duration: "90 minutes"
next_course: "/courses/02-entities-value-objects/"
next_title: "Entities and Value Objects"
order: 1
---

# Event Storming and Contexts

**Goal:** Discover the domain language, the important events, where things can fail, and how to slice the system.

## Workshop Instructions

**Do this:**
* Put orange notes for domain events. Use the past tense: AccountRegistered, AccountFollowed, AccountBlocked, FollowerRemoved.
* Add blue notes for commands that cause them: RegisterAccount, FollowAccount, BlockAccount, RemoveFollower.
* Add pink notes for failure events: AccountAlreadyExists, FollowRejectedBlocked, FollowRejectedSelf.
* Add yellow notes for actors: EndUser, Moderator.
* Cluster green notes for entities: Account, Follow.
* Draw boundaries: Accounts context, SocialGraph context. Keep posting out of scope today.

## Minimal Golden Path

```
RegisterAccount -> AccountRegistered
FollowAccount   -> AccountFollowed
BlockAccount    -> AccountBlocked -> (policy) RemoveFollower -> FollowerRemoved
```

## Domain for Practice

We'll build a **minimal social app** where:
- Users register accounts
- Users follow each other  
- Users can block other users
- **The classic bug:** if B blocks A, A still sees B's posts because the follow link remains

We'll use a policy to fix this bug during the workshop.

## Deliverables

By the end of this session you should have:

1. **Photo or screenshot** of the sticky board
2. **List of events:** AccountRegistered, AccountFollowed, AccountBlocked, FollowerRemoved
3. **List of commands:** RegisterAccount, FollowAccount, BlockAccount, RemoveFollower  
4. **List of entities:** Account, Follow
5. **First cut of bounded contexts:** Accounts context, SocialGraph context

## Three-Step Improvement Pattern

**Immediate patch:** Make failure events explicit.

**Deeper cause:** Hidden rules. Ask: under what conditions must this not happen?

**Optional improvement:** Add hot path metrics on the board: volume, frequency, latency targets.

## Exercises

### Event Storming Practice
* Add fail events for every command. Example: BlockRejectedUnknownAccount.
* Add actors who trigger each command.
* Split the board into Accounts and SocialGraph contexts. Draw arrows only where events cross a boundary.

**Immediate patch:** Mark one happy path end to end.

**Deeper cause:** Too much scope. Cut posting and liking for now.

**Optional improvement:** Tag commands with expected frequency to guide storage choices later.

---

**Next:** [Part 2 - Entities and Value Objects](/courses/02-entities-value-objects/) - Learn to represent the ubiquitous language in code using events to derive attributes.
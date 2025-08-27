---
layout: post
title: "Factories and Object Construction in Python (Game Example)"
date: 20225-08-26 09:30:00 +1000
categories: python
---

I don’t like constructors that can fail. Once you call __init__, you’ve already created the object. If something goes
wrong in there, the only option is to throw an exception. That makes the whole codebase fragile—especially if other code
assumes construction always works. A safer way is to move risky or conditional logic into a factory.

### A Game Example: Bullets

Let’s say we’re making a game, and we have a Bullet class:

```python
class Bullet:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.active = True
```

Naively, you might just create new bullets every time the player shoots:

```python
def shoot():
    return Bullet((0, 0), (1, 0))
```

But in a real game, bullets are created and destroyed constantly. Allocating new objects every time is expensive. Worse,
you might run into resource limits.

### Factory with a Pool

A factory can help here. Instead of always constructing a new Bullet, it can reuse old ones from a pool.

```python
class Bullet:
    def __init__(self):
        self.position = (0, 0)
        self.velocity = (0, 0)
        self.active = False

    def reset(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.active = True


class BulletFactory:
    def __init__(self, pool_size=100):
        self.pool = [Bullet() for _ in range(pool_size)]

    def create(self, position, velocity):
        for bullet in self.pool:
            if not bullet.active:
                bullet.reset(position, velocity)
                return bullet
        return None  # no free bullets
```

Now you’re not committed to always constructing a brand new object. Sometimes you just recycle an existing one.

### Using the Factory

```python
factory = BulletFactory(pool_size=3)

b1 = factory.create((0, 0), (1, 0))
b2 = factory.create((1, 0), (1, 0))
b3 = factory.create((2, 0), (1, 0))
b4 = factory.create((3, 0), (1, 0))  # returns None, pool exhausted

print(b1, b2, b3, b4)
```

Output:

```shell
<Bullet object at ...>
<Bullet object at ...>
<Bullet object at ...>
None
```

Construction itself is never failing. The factory decides whether it’s possible to hand you a new (or recycled) object.

### Why This Works Well

* `Bullet.__init__` is simple and guaranteed to succeed.
* The creation logic (allocation, pooling, limits) lives in the factory.
* You can later swap the factory logic—bigger pool, smarter recycling—without touching the Bullet class or other code
  that uses it.

Factories aren’t about moving constructor logic around. They’re about handling cases where construction isn’t guaranteed
or where allocation strategies vary. In games, this comes up all the time: bullets, enemies, projectiles, particles. But
the same principle applies anywhere resources are limited—connections, workers, even threads.

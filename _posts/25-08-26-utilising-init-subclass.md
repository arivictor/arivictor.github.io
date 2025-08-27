---
layout: post
title: "Utilising __init_subclass__ Before Metaclasses"
date: 2025-08-26 10:30:00 +1000
categories: python
---

I used to default to metaclasses any time I wanted custom behaviour when defining subclasses. Then I stumbled across
`__init_subclass__` and realised it solved most of the problems I was reaching for metaclasses for. Since Python 3.6
it’s been there, built-in, and in practice I’ve found it covers the majority of my use cases.

### What It Does

`__init_subclass__` is a hook that runs on the base class whenever a subclass is defined. Think of it as `__init__`, but
for class definitions rather than instances.

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"Defining subclass: {cls.__name__}")


class Child(Base):
    pass
```

Output:

```shell
"Defining subclass: Child"
```

One method, no metaclass boilerplate.

### Why I Started Using It

For me, the appeal is that it keeps logic close to where it belongs, inside the base class, without introducing extra
machinery. It’s lightweight, obvious to readers, and easy to drop in when I want behaviour triggered at subclass
definition.

### A Few Cases Where It Helped

#### 1. Auto-registering subclasses

I had a plugin system where every plugin needed to register itself. I used to keep a separate registry function, but
with __init_subclass__, the base class handles it neatly.

```python
class PluginBase:
    plugins = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"Registering: {cls.__name__}")
        PluginBase.plugins.append(cls)


class PluginA(PluginBase):
    pass


class PluginB(PluginBase):
    pass


print(PluginBase.plugins)
```

Output:

```shell
Registering: PluginA
Registering: PluginB
[<class '__main__.PluginA'>, <class '__main__.PluginB'>]
```

No separate global registry code. Just subclasses doing their thing.

#### 2. Catching mistakes early

In one case I needed every subclass to define a foo method. __init_subclass__ let me raise errors right when the class
is defined, rather than waiting until runtime when something breaks.

```
class RequiresFoo:
    def __init_subclass__(cls):
        super().__init_subclass__()
        if 'foo' not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define a 'foo' method")

class Good(RequiresFoo):
    def foo(self):
        pass

class Bad(RequiresFoo):
    pass  # Raises TypeError
```

This made missing implementations show up instantly, which saved me a couple of debugging sessions.

### When It Wasn’t Enough

It’s not a total replacement for metaclasses. Times I still needed a metaclass:
• actually altering the class creation process (changing __new__, tweaking type())
• injecting descriptors or playing with the MRO
• more complex multi-inheritance hooks

So if you need to reshape how classes are built, you’re still in metaclass land. But if you just want to respond to
subclasses being defined, __init_subclass__ is usually enough. Now, whenever I find myself about to declare a metaclass
just to do something like tracking subclasses, enforcing rules, or adding attributes, I try __init_subclass__ first.
Most of the time, it does exactly what I need, and the code ends up smaller and easier to follow. That’s been my
experience so far. If you’ve used it in bigger frameworks or DSLs, I’d be curious to hear how it compared to metaclasses
in your case.

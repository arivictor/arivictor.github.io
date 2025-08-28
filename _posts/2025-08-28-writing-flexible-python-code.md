---
layout: post
title: "Writing Flexible Python Code"
description: 'How I try to keep my Python code flexible by minimising the surface area of changes'
date: 2025-08-28
categories: ["python"]
---

One idea I try to keep in mind when writing Python is minimising surface area. To me, that means when I add or change a feature, I don’t want it to ripple out and force changes across unrelated parts of the code. The smaller the impact of a change, the more comfortable I feel making it.

### A First Attempt

Say I’ve got a little `Product` class:

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.discount = None
```

At first, I just need to support one discount per product, so I add a discount attribute.

But then someone asks: _“Yo Ari, can we support percentage discounts as well as fixed amount discounts?”_

So of course I start bolting things on:

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.discount_amount = None
        self.discount_percent = None
```

Now I’ve tangled discount logic directly into the `Product` class. If I want to add promotional discounts, like _“buy one get one free”_, I’ll be back here again, slapping on more attributes and conditionals.

## Pulling It Out

What works better I have found is pulling the discount logic out into its own thing:

```python
class Discount:
    def apply(self, price):
        return price


class FixedDiscount(Discount):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, price):
        return price - self.amount


class PercentDiscount(Discount):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, price):
        return price * (1 - self.percent)
```

Now `Product` doesn’t need to care about the details. I think this covers the S and O in SOLID principles.

```python
class Product:
    def __init__(self, name, price, discount=None):
        self.name = name
        self.price = price
        self.discount = discount

    def final_price(self):
        if self.discount:
            return self.discount.apply(self.price)
        return self.price
```

Using it:

```python
p1 = Product("Coffee Mug", 12.0, PercentDiscount(0.2))
p2 = Product("T-Shirt", 25.0, FixedDiscount(5))

print(p1.final_price())  # 9.6
print(p2.final_price())  # 20
```

If later I want to add another _“Buy One Get One Free”_ discount, I just create another class. I don’t touch Product at all.

## Why I Like This

This keeps the Product class small and predictable. All the churn happens in Discount, which is exactly where I expect it.

If I delete discounts tomorrow, I can remove the Discount classes and one attribute from Product. The rest of the system still works.

That’s what minimising surface area feels like to me, features evolve in their own space instead of constantly seeping into core objects.

When I write Python, I often think:

- If I extend this feature, will I end up rewriting something unrelated?
- If I remove it, does the rest of the code still make sense?
- Can someone else add a new variation without breaking existing code?

If the answers are yes, then the design feels right.

I don’t treat this as a rule, more like a habit I’ve picked up. When features are isolated, the code feels lighter, less fragile. I don’t dread changes as much, and my teammates can dive in without me handholding them.

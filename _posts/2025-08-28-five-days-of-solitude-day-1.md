---
layout: post
title: "Five Days Of Solitude: Day 1 - Single Responsibility Principle (SRP)"
description: 'How I spent five days locked away with Python, coffee, and the determination to get better at design. Day 1: Single Responsibility Principle (SRP)'
date: 2025-08-28
categories: python solid design day-1 srp
---

For five days I locked myself away with nothing but Python, coffee, and the determination to get better at design. No slack, no meetings, no distractions, just one with the code.

I planned to revisit and lock down the SOLID principles. These five rules of object-oriented design have been around for decades, but they’re still as useful today as when they were first put to words. They help keep code simple, flexible, and maintainable, even when projects grow messy.

Each day in solitude I explored one of them. Each day, I wrote Python examples, thought about how the principle shows up in real projects, and how it keeps code from turning into a ball of *"wtf is this?"*.

What follows is the record of my retreat. Five days, five principles, and a reminder that sometimes stepping away from the noise is the best way to sharpen your craft.

### Day 1: Single Responsibility Principle (SRP)

The Single Responsibility Principle says a class should have one reason to change.

That sounds simple, but it’s the difference between code you can live with and code that drives you mad.

Imagine this:

```python
class ReportManager:
    def __init__(self, content):
        self.content = content

    def generate(self):
        return f"Report: {self.content}"

    def save(self, filename):
        with open(filename, "w") as f:
            f.write(self.generate())

    def email(self, to):
        print(f"Sending report to {to}")
```

Looks pretty conventional, but this class has three reasons to change:

* Report formatting changes.
* File saving logic changes.
* Email delivery changes.

That’s three headaches waiting for you.

A better way:

```python
class Report:
    def __init__(self, content):
        self.content = content

    def generate(self):
        return f"Report: {self.content}"

class FileSaver:
    def save(self, report, filename):
        with open(filename, "w") as f:
            f.write(report.generate())

class EmailSender:
    def send(self, report, to):
        print(f"Sending {report.generate()} to {to}")
```

Now, each class has one job. One reason to change.

Let's recap:

* If a class is responsible for formatting a report, then the only reason to change it should be when the formatting rules change.
* If a class is responsible for saving files, the only reason to change it should be when the file storage logic changes.
* If a class is responsible for sending emails, the only reason to change it should be when the email delivery method changes.

The mistake comes when one class handles all of these. Then it has multiple reasons to change (formatting rules, file I/O requirements, email transport changes). That violates SRP.
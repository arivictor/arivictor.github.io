---
layout: post
title: "The S in SOLID, with code"
description: 'One reason to change. Nothing more.'
date: 2025-08-28 12:00:00 +1000
tags:
    - python
    - solid
---

Single Responsibility Principle.
One reason to change. Nothing more.

## Definition

A module should do one thing.
A class or function should have one reason to change.

## Why it matters

Smaller surface area.
Easier tests.
Cheaper changes.
Clear ownership of behaviour.

## Anti example

```python
import json
from pathlib import Path
from datetime import datetime

class ReportManager:
    def __init__(self, path: Path):
        self.path = path
        self.items = []

    def add_item(self, item: dict):
        self.items.append(item)

    def total(self) -> float:
        return sum(x["amount"] for x in self.items)

    def to_markdown(self) -> str:
        lines = ["# Report", f"Generated: {datetime.utcnow().isoformat()}"]
        for x in self.items:
            lines.append(f"- {x['name']}: ${x['amount']:.2f}")
        lines.append(f"Total: ${self.total():.2f}")
        return "\n".join(lines)

    def save(self):
        # mixes formatting, IO, and domain
        md = self.to_markdown()
        self.path.write_text(md, encoding="utf-8")

    def export_json(self):
        data = {"items": self.items, "total": self.total()}
        self.path.with_suffix(".json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
```

Problems:

1. Domain logic lives with formatting and file IO.
2. Any change to output format or storage touches the same class.
3. Hard to test in isolation.

## SRP refactor

Split by reason to change.

* Domain
* Presentation
* Persistence

```python
from dataclasses import dataclass
from typing import Iterable, Protocol
from pathlib import Path
import json
from datetime import datetime

# Domain

@dataclass(frozen=True)
class LineItem:
    name: str
    amount: float

@dataclass
class Report:
    items: list[LineItem]

    def total(self) -> float:
        return sum(x.amount for x in self.items)


# Presentation

class Formatter(Protocol):
    def format(self, report: Report) -> str: ...

class MarkdownFormatter:
    def format(self, report: Report) -> str:
        parts = [
            "# Report",
            f"Generated: {datetime.utcnow().isoformat()}",
            *[f"- {x.name}: ${x.amount:.2f}" for x in report.items],
            f"Total: ${report.total():.2f}",
        ]
        return "\n".join(parts)

class JsonFormatter:
    def format(self, report: Report) -> str:
        payload = {
            "items": [{"name": x.name, "amount": x.amount} for x in report.items],
            "total": report.total(),
        }
        return json.dumps(payload, indent=2)


# Persistence

class Writer(Protocol):
    def write(self, content: str) -> None: ...

class FileWriter:
    def __init__(self, path: Path):
        self.path = path

    def write(self, content: str) -> None:
        self.path.write_text(content, encoding="utf-8")


# Application orchestration

def render_and_write(report: Report, formatter: Formatter, writer: Writer) -> None:
    writer.write(formatter.format(report))

Usage

report = Report(items=[LineItem("Widget", 12.5), LineItem("Gadget", 7.5)])

# Markdown to file
render_and_write(
    report,
    MarkdownFormatter(),
    FileWriter(Path("report.md")),
)

# JSON to file
render_and_write(
    report,
    JsonFormatter(),
    FileWriter(Path("report.json")),
)
```

Benefits
1. Change formatting without touching domain or IO.
2. Swap storage easily. Add S3Writer or StdoutWriter without touching Report or formatters.
3. Test each piece alone.

Testing in isolation

```python
class StubWriter:
    def __init__(self):
        self.payload = None
    def write(self, content: str) -> None:
        self.payload = content

def test_markdown_formatting():
    r = Report([LineItem("Item", 10)])
    w = StubWriter()
    render_and_write(r, MarkdownFormatter(), w)
    assert "Total: $10.00" in w.payload

def test_total_only_domain():
    r = Report([LineItem("A", 1.0), LineItem("B", 2.5)])
    assert r.total() == 3.5
```

No filesystem in tests. No datetime stubbing outside the formatter if you choose to inject a clock later.

## Finding SRP violations

Heuristics

1. Method names refer to different concerns. Example format, save, validate inside one class.
2. More than one stakeholder asks for changes in the same class. Example design asks for layout changes, ops asks for path changes.
3. Hard to name the class without using the word and.

When to stop splitting

* Do not chase perfection. Split by real reasons to change.
* If two concerns always change together, keep them together.
* SRP is a guide to reduce blast radius, not a rule to inflate class counts.

## Summary

One class. One reason to change.
Keep domain pure.

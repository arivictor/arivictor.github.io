---
layout:     post
title:      "Import Organization: Small Changes, Big Impact"
date:       2024-12-30
summary:    How I learned that the way you organize imports reveals everything about code quality
categories: python imports organization code-quality
---

The first thing I notice when reviewing Python code isn't the logic or the algorithms—it's the imports.

```python
from datetime import datetime
import sys
from typing import List, Dict
import requests
from .utils import helper_function
import os
from models import User
from django.contrib import admin
```

This tells me everything I need to know about the codebase. If imports are a mess, the rest of the code probably is too.

## Why import organization matters

Imports are the first code a reader encounters. They set expectations about:

- **Dependencies**: What external libraries does this module rely on?
- **Architecture**: How does this module fit into the larger system?
- **Scope**: Is this a focused module or does it do everything?
- **Maintenance**: How easy will this be to update or refactor?

Messy imports signal technical debt before you even get to the business logic.

## The import hierarchy I follow

I organize imports in four groups, separated by blank lines:

```python
# 1. Standard library imports
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party imports
import requests
from sqlalchemy import create_engine
from pydantic import BaseModel

# 3. Local application imports
from .config import settings
from .database import get_connection
from .models import User, Task

# 4. Relative imports (if needed)
from . import utils
from ..shared import constants
```

This hierarchy follows Python's import resolution order and makes dependencies crystal clear.

## Specific techniques that improved my code

**Absolute imports over relative:**
```python
# Instead of this
from . import models
from ..utils import helper

# Do this
from myapp.models import User
from myapp.utils import helper_function
```

Absolute imports make code more explicit and easier to refactor.

**Import specific names, not modules:**
```python
# Instead of this
import datetime
import typing

start_time = datetime.datetime.now()
users: typing.List[str] = []

# Do this
from datetime import datetime
from typing import List

start_time = datetime.now()
users: List[str] = []
```

More readable and shows exactly what you're using.

**Group related imports:**
```python
# Database-related imports together
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command

# API-related imports together  
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
```

This makes it easy to see all dependencies for a particular concern.

## When to break the rules

**Large applications with many internal modules:**
```python
# Sometimes it's clearer to group by functionality
from myapp.auth import authenticate, authorize
from myapp.database import User, Task, Project
from myapp.email import send_notification
from myapp.utils import format_date, parse_json
```

**Testing modules:**
```python
# Test imports often need different organization
import pytest
from unittest.mock import Mock, patch

from myapp.models import User
from myapp.services import UserService

from .factories import UserFactory
from .helpers import create_test_database
```

**Scripts and one-off tools:**
```python
#!/usr/bin/env python3
# Quick scripts can be more relaxed
import sys
import argparse
from pathlib import Path
from myapp.utils import process_file

if __name__ == "__main__":
    # Script logic here
```

## Managing import complexity

**Use `__init__.py` to control public APIs:**
```python
# myapp/models/__init__.py
from .user import User
from .task import Task
from .project import Project

# Now other modules can import cleanly
from myapp.models import User, Task, Project
```

**Avoid star imports in production code:**
```python
# Don't do this
from myapp.models import *
from typing import *

# Do this
from myapp.models import User, Task
from typing import Dict, List, Optional
```

Star imports make it impossible to track where names come from.

**Use type-checking imports for complex types:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.complex_module import ComplexClass

def process_data(data: 'ComplexClass') -> None:
    # Function implementation
```

This avoids circular imports while keeping type hints.

## Tools that enforce consistency

**isort** for automatic import sorting:
```bash
pip install isort
isort --profile black myapp/
```

Configuration in `pyproject.toml`:
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["myapp"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

**flake8-import-order** for linting:
```bash
pip install flake8-import-order
flake8 --import-order-style=google myapp/
```

**Pre-commit hooks** to enforce automatically:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

## Common anti-patterns I avoid

**The everything import:**
```python
# Signals poor module design
from myapp.utils import (
    helper1, helper2, helper3, helper4, helper5,
    helper6, helper7, helper8, helper9, helper10
)
```

If you need this many imports from one module, the module is doing too much.

**Circular imports disguised as relative imports:**
```python
# myapp/models/user.py
from ..services.user_service import process_user  # Circular dependency

# myapp/services/user_service.py  
from ..models.user import User
```

This usually indicates poor separation of concerns.

**Import-time side effects:**
```python
# Don't do this
import myapp.config  # This immediately connects to database

# Do this instead
from myapp.config import get_database_url
```

Imports should be declarative, not imperative.

## The refactoring test

When I refactor code, imports tell me how hard it will be:

**Easy to refactor:**
```python
from datetime import datetime
from typing import List

from myapp.models import User
from myapp.services import EmailService
```

Clear dependencies, focused purpose.

**Hard to refactor:**
```python
import myapp.everything
from myapp.utils import *
from .helpers import helper1, helper2, helper3, helper4
```

Too many dependencies, unclear boundaries.

## The team impact

Good import organization has team benefits:

- **Code reviews are faster**: Easy to spot new dependencies
- **Onboarding is smoother**: New developers understand module relationships
- **Refactoring is safer**: Clear dependency graphs prevent breakage
- **Testing is easier**: Fewer import-related test failures

## My import checklist

Before committing code, I check:

1. **Are imports grouped logically?** Standard library, third-party, local
2. **Are they sorted alphabetically within groups?** Consistency helps readability
3. **Do I import only what I use?** Unused imports add cognitive load
4. **Are import names specific?** `from module import function` vs `import module`
5. **Will these imports make sense in 6 months?** Clear naming and organization

## The bottom line

Import organization seems trivial until you're maintaining a large codebase. Clean imports signal:

- Thoughtful design
- Clear dependencies  
- Maintainable code
- Professional standards

Start with imports. They set the tone for everything that follows.

Good code starts at the top of the file.
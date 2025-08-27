---
layout:     post
title:      Error Handling That Actually Helps Your Future Self
date:       2025-01-02
summary:    Moving beyond generic try/except blocks to error handling that makes debugging a pleasure instead of a nightmare
categories: python exceptions error-handling debugging
---

Six months ago, I got paged at 2 AM because our data pipeline was failing. The error message? "Something went wrong."

That was the moment I realized my error handling was garbage.

## The problem with generic exception handling

Most Python code I see (including my own, historically) treats exceptions like an afterthought:

```python
def process_user_data(user_id):
    try:
        user = get_user(user_id)
        data = fetch_user_data(user)
        result = transform_data(data)
        save_result(result)
        return result
    except Exception as e:
        logger.error(f"Error processing user {user_id}: {e}")
        return None
```

This tells me nothing useful when things break. Did the user not exist? Was the API down? Did the transformation fail? Was the database unreachable?

## Error handling that tells a story

Good error handling should tell you three things:
1. **What** went wrong
2. **Where** it went wrong  
3. **What** you can do about it

Here's how I've learned to structure exceptions:

```python
class DataProcessingError(Exception):
    """Base exception for data processing operations."""
    pass

class UserNotFoundError(DataProcessingError):
    """Raised when a user doesn't exist in the system."""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")

class DataFetchError(DataProcessingError):
    """Raised when external data can't be retrieved."""
    def __init__(self, service, user_id, original_error):
        self.service = service
        self.user_id = user_id
        self.original_error = original_error
        super().__init__(
            f"Failed to fetch data from {service} for user {user_id}: {original_error}"
        )

class TransformationError(DataProcessingError):
    """Raised when data transformation fails."""
    def __init__(self, stage, data_sample, original_error):
        self.stage = stage
        self.data_sample = data_sample[:100]  # First 100 chars for debugging
        self.original_error = original_error
        super().__init__(
            f"Transformation failed at {stage}: {original_error}"
        )
```

Now the processing function becomes:

```python
def process_user_data(user_id):
    try:
        user = get_user(user_id)
    except UserNotFound:
        raise UserNotFoundError(user_id)
    
    try:
        data = fetch_user_data(user)
    except APIError as e:
        raise DataFetchError("user-service", user_id, e)
    
    try:
        result = transform_data(data)
    except (ValueError, KeyError) as e:
        raise TransformationError("data_normalization", str(data), e)
    
    try:
        save_result(result)
    except DatabaseError as e:
        logger.error(f"Failed to save result for user {user_id}: {e}")
        # Re-raise because this might be temporary
        raise
    
    return result
```

## Context preservation with exception chaining

Python 3's `raise ... from ...` syntax preserves the full error chain:

```python
def parse_config_file(filename):
    try:
        with open(filename) as f:
            content = f.read()
    except FileNotFoundError as e:
        raise ConfigurationError(f"Config file {filename} not found") from e
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid JSON in config file {filename}"
        ) from e
```

This gives you both the high-level context and the low-level details when debugging.

## Retry logic that doesn't hide problems

Retries are common in distributed systems, but naive retry logic can mask real issues:

```python
# Don't hide failures like this
def fetch_data_with_retry(url, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return requests.get(url).json()
        except:
            if attempt == max_attempts - 1:
                return None  # Silent failure!
            time.sleep(2 ** attempt)
```

Instead, be explicit about what you're retrying and why:

```python
class RetryableError(Exception):
    """Base class for errors that should be retried."""
    pass

class TemporaryServiceError(RetryableError):
    """Service is temporarily unavailable."""
    pass

class RateLimitError(RetryableError):
    """Rate limit exceeded."""
    pass

def fetch_data_with_retry(url, max_attempts=3):
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout as e:
            last_error = TemporaryServiceError(f"Timeout on attempt {attempt + 1}") from e
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                last_error = RateLimitError(f"Rate limited on attempt {attempt + 1}") from e
            elif 500 <= e.response.status_code < 600:
                last_error = TemporaryServiceError(f"Server error {e.response.status_code}") from e
            else:
                # Don't retry client errors
                raise
        
        if attempt < max_attempts - 1:
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {last_error}")
            time.sleep(wait_time)
    
    # All attempts failed
    raise last_error
```

## Structured logging for debugging

Combine good exception handling with structured logging:

```python
import structlog

logger = structlog.get_logger()

def process_user_data(user_id):
    logger.info("Starting user data processing", user_id=user_id)
    
    try:
        user = get_user(user_id)
        logger.info("User retrieved", user_id=user_id, username=user.username)
        
        data = fetch_user_data(user)
        logger.info("User data fetched", user_id=user_id, data_size=len(data))
        
        result = transform_data(data)
        logger.info("Data transformed", user_id=user_id, result_type=type(result).__name__)
        
        save_result(result)
        logger.info("Processing completed", user_id=user_id)
        
        return result
        
    except UserNotFoundError:
        logger.warning("User not found", user_id=user_id)
        raise
        
    except DataFetchError as e:
        logger.error(
            "Data fetch failed", 
            user_id=user_id,
            service=e.service,
            error=str(e.original_error)
        )
        raise
        
    except Exception:
        logger.exception("Unexpected error during processing", user_id=user_id)
        raise
```

## Error recovery patterns

Sometimes you can recover from errors gracefully:

```python
def get_user_preferences(user_id):
    """Get user preferences with fallback to defaults."""
    try:
        return fetch_user_preferences(user_id)
    except PreferencesNotFoundError:
        logger.info("No preferences found, using defaults", user_id=user_id)
        return get_default_preferences()
    except PreferencesServiceError as e:
        logger.warning(
            "Preferences service unavailable, using defaults",
            user_id=user_id,
            error=str(e)
        )
        return get_default_preferences()

def batch_process_with_partial_failure(items):
    """Process items individually, collecting both successes and failures."""
    results = []
    errors = []
    
    for item in items:
        try:
            result = process_item(item)
            results.append(result)
        except ProcessingError as e:
            logger.warning("Item processing failed", item_id=item.id, error=str(e))
            errors.append((item.id, e))
    
    if errors:
        logger.info(
            "Batch completed with partial failures",
            success_count=len(results),
            error_count=len(errors)
        )
    
    return results, errors
```

## The debugging payoff

Good error handling pays dividends when things go wrong. Instead of spending hours reproducing issues, you get:

- Clear error messages that point to the root cause
- Preserved context through exception chaining  
- Structured logs that tell the story of what happened
- Graceful degradation when possible

That 2 AM page I mentioned? It doesn't happen anymore. When errors occur, the logs tell me exactly what went wrong and where to look.

## My error handling checklist

Before shipping code, I ask:

1. **Are my exceptions specific?** Generic `Exception` catches hide problems.
2. **Do my error messages include context?** User IDs, file paths, API endpoints—whatever helps debugging.
3. **Am I preserving the original error?** Use `raise ... from ...` to maintain the error chain.
4. **Are my retries intelligent?** Only retry what makes sense to retry.
5. **Are my logs searchable?** Structured logging beats string concatenation.

Good error handling isn't about preventing all errors—it's about making the inevitable errors easy to understand and fix.

Your future self will thank you when the inevitable 2 AM page comes in.
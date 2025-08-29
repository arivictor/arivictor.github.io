# Dynamic Tag System

This site uses a dynamic tag system that automatically generates tag pages based on the tags found in blog posts.

## How it works

1. **Tag Detection**: The `generate_tags.py` script scans all posts in `_posts/` and extracts unique tags
2. **Page Generation**: For each found tag, it creates a corresponding tag page in `tags/`
3. **Layout**: Each tag page uses the `tag.html` layout to display all posts with that tag

## Usage

### Automatic Generation

The tag generation is integrated into the build process:

```bash
# Generate tags and serve the site
make serve

# Generate tags and build the site
make build

# Generate tags manually
make generate-tags
```

### Adding New Tags

1. Add tags to any post in the front matter:
   ```yaml
   ---
   title: "My Post"
   tags:
     - python
     - new-tag
   ---
   ```

2. Run the tag generator:
   ```bash
   make generate-tags
   ```

3. The new tag page will be automatically created

### Benefits

- **Scalable**: No need to manually create tag pages
- **Automatic**: Detects all tags used in posts
- **Clean**: Removes unused tag pages
- **GitHub Pages Compatible**: Uses standard Jekyll features

## Files

- `generate_tags.py` - Script that generates tag pages
- `_layouts/tag.html` - Layout template for tag pages  
- `tags/index.md` - Index of all tags
- `tags/*.md` - Individual tag pages (generated)
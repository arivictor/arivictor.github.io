#!/usr/bin/env python3
"""
Generate tag pages dynamically based on tags found in posts.
This script scans all posts for tags and creates individual tag pages.
"""

import os
import re
import yaml
from pathlib import Path

def extract_tags_from_posts():
    """Extract all unique tags from posts in _posts directory."""
    posts_dir = Path("_posts")
    all_tags = set()
    
    if not posts_dir.exists():
        print("_posts directory not found")
        return all_tags
    
    for post_file in posts_dir.glob("*.md"):
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract front matter
        front_matter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if front_matter_match:
            try:
                front_matter = yaml.safe_load(front_matter_match.group(1))
                if 'tags' in front_matter and isinstance(front_matter['tags'], list):
                    all_tags.update(front_matter['tags'])
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {post_file}: {e}")
    
    return sorted(all_tags)

def create_tag_page(tag):
    """Create an individual tag page."""
    tags_dir = Path("tags")
    tags_dir.mkdir(exist_ok=True)
    
    tag_file = tags_dir / f"{tag}.md"
    
    content = f"""---
layout: tag
tag: {tag}
permalink: /tags/{tag}/
---"""
    
    with open(tag_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created tag page: {tag_file}")

def clean_old_tag_pages():
    """Remove existing tag pages (except index.md)."""
    tags_dir = Path("tags")
    if not tags_dir.exists():
        return
        
    for tag_file in tags_dir.glob("*.md"):
        if tag_file.name != "index.md":
            tag_file.unlink()
            print(f"Removed old tag page: {tag_file}")

def main():
    """Main function to generate tag pages."""
    print("Generating tag pages...")
    
    # Extract tags from posts
    tags = extract_tags_from_posts()
    if not tags:
        print("No tags found in posts")
        return
    
    print(f"Found tags: {', '.join(tags)}")
    
    # Clean old tag pages
    clean_old_tag_pages()
    
    # Create new tag pages
    for tag in tags:
        create_tag_page(tag)
    
    print(f"Generated {len(tags)} tag pages")

if __name__ == "__main__":
    main()
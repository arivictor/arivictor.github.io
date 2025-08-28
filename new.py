import sys
import os
from datetime import datetime

def sanitise_filename(filename):
    # Replace spaces with hyphens and convert to lowercase
    return filename.strip().replace(" ", "-").lower()

def create_post(filename):
    # Ensure the _posts directory exists
    filename = sanitise_filename(filename)
    
    posts_dir = "_posts"
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)

    # Get the current date for the filename
    today = datetime.now().strftime("%Y-%m-%d")
    jekyll_filename = f"{today}-{filename}.md"
    filepath = os.path.join(posts_dir, jekyll_filename)

    # Create the markdown content
    title = filename.replace("-", " ").title()
    content = """---
layout: post
title: "{title}"
date: {today}
categories: []
---

# {title}
Write your content here.
        """.format(title=title, today=today)


    # Write the file
    with open(filepath, "w") as file:
        file.write(content) 

        print(f"Post created: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python new.py <filename>")
        sys.exit(1)

    create_post(sys.argv[1])
#!/usr/bin/env python3
"""Simple static blog generator."""

import yaml
from pathlib import Path


def load_posts():
    """Load posts from YAML file."""
    data_path = Path(__file__).parent / "data" / "posts.yaml"
    with open(data_path, "r") as f:
        return yaml.safe_load(f)["posts"]


def generate_index(site_name="blog", tagline="Thoughts on technology and AI"):
    """Generate the index page."""
    posts = load_posts()

    post_html = ""
    for post in posts:
        post_html += f"""
<div class="post-item">
    <h2><a href="posts/{post["title"].lower().replace(" ", "-")}.html">{post["title"]}</a></h2>
    <p class="post-meta">{post["date"]}</p>
    <p class="post-excerpt">{post.get("excerpt", post["content"][:150])}...</p>
</div>
"""

    template = Path(__file__).parent / "templates" / "index.html"
    with open(template, "r") as f:
        content = f.read()

    return (
        content.replace("{title}", site_name)
        .replace("{site_name}", site_name)
        .replace("{tagline}", tagline)
        .replace("{posts}", post_html)
        .replace('href="/', 'href="./')
        .replace('src="/', 'src="./')
    )


def generate_post(post):
    """Generate a single blog post page."""
    template = Path(__file__).parent / "templates" / "post.html"
    with open(template, "r") as f:
        content = f.read()

    return (
        content.replace("{title}", post["title"])
        .replace("{site_name}", "blog")
        .replace("{post.title}", post["title"])
        .replace("{post.date}", post["date"])
        .replace("{post.content}", post["content"])
        .replace('href="/', 'href="../')
        .replace('src="/', 'src="../')
    )


def generate_static_files():
    """Generate all static HTML files."""
    output_dir = Path(__file__).parent / "public"

    # Generate index
    with open(output_dir / "index.html", "w") as f:
        f.write(generate_index())

    # Generate each post
    for post in load_posts():
        filename = post["title"].lower().replace(" ", "-") + ".html"
        with open(output_dir / "posts" / filename, "w") as f:
            f.write(generate_post(post))

    # Copy about and projects pages (with viewport and relative paths)
    (output_dir / "about.html").write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About | blog</title>
    <link rel="stylesheet" href="./styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="./index.html" class="logo">blog</a>
            <ul class="nav-links">
                <li><a href="./index.html">Home</a></li>
                <li><a href="./about.html">About</a></li>
                <li><a href="./projects.html">Projects</a></li>
            </ul>
        </div>
    </nav>

    <main class="container about-content">
        <h1>About</h1>
        <p>This is a simple personal blog built with minimal static HTML and CSS.</p>
        
        <h2>Design Philosophy</h2>
        <p>The design focuses on readability and simplicity. No JavaScript, no tracking, just clean typography.</p>
        
        <h2>Built With</h2>
        <ul>
            <li>HTML5</li>
            <li>CSS3</li>
            <li>Python for generation</li>
        </ul>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2026 blog. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>""")

    (output_dir / "projects.html").write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects | blog</title>
    <link rel="stylesheet" href="./styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="./index.html" class="logo">blog</a>
            <ul class="nav-links">
                <li><a href="./index.html">Home</a></li>
                <li><a href="./about.html">About</a></li>
                <li><a href="./projects.html">Projects</a></li>
            </ul>
        </div>
    </nav>

    <main class="container projects-list">
        <h1>Projects</h1>
        
        <div class="project-item">
            <h2>Personal Blog</h2>
            <p>This minimal blog platform built with static HTML and Python.</p>
            <a href="./index.html">View project &rarr;</a>
        </div>
        
        <div class="project-item">
            <h2>More Coming Soon</h2>
            <p>I'll add more projects here in the future.</p>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2026 blog. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>""")

    # Create posts directory and copy posts
    (output_dir / "posts").mkdir(exist_ok=True)


if __name__ == "__main__":
    generate_static_files()
    print("Blog generated successfully!")

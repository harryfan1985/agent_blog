#!/usr/bin/env python3
"""Modern static blog generator with enhanced features."""

import yaml
import re
from pathlib import Path
from datetime import datetime


NAV_SCROLL_JS = """
    <script>
    (function() {
        var navbar = document.querySelector('.navbar');
        if (!navbar) return;
        var lastScroll = 0;
        var ticking = false;

        function updateNavbar() {
            var currentScroll = window.pageYOffset || document.documentElement.scrollTop;
            if (currentScroll <= 0) {
                navbar.classList.remove('hidden');
                ticking = false;
                return;
            }
            if (currentScroll > lastScroll && currentScroll > 64) {
                navbar.classList.add('hidden');
            } else {
                navbar.classList.remove('hidden');
            }
            lastScroll = currentScroll <= 0 ? 0 : currentScroll;
            ticking = false;
        }

        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        }, { passive: true });
    })();
    </script>"""


def load_posts():
    data_path = Path(__file__).parent / "data" / "posts.yaml"
    with open(data_path, "r") as f:
        posts = yaml.safe_load(f)["posts"]

    for post in posts:
        if "title" not in post:
            content = post.get("content", "")
            match = re.search(r'<h1>([^<]+)</h1>', content)
            post["title"] = match.group(1) if match else "Untitled"

        if "date" not in post:
            match = re.search(r'发布日期[：:]\s*([^<\n]+)', post.get("content", ""))
            post["date"] = match.group(1).strip() if match else "Unknown"

        if "excerpt" not in post:
            text = re.sub(r'<[^>]+>', '', post.get("content", ""))
            post["excerpt"] = text[:200].strip()

    return posts


def slugify(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s]', '-', slug)
    slug = slug.replace(' ', '-')
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def estimate_read_time(content):
    text = re.sub(r'<[^>]+>', '', content)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    minutes = max(1, round((chinese_chars + english_words) / 400))
    return f"{minutes} 分钟阅读"


def generate_index(site_name="Agent Blog", tagline="探索 AI Agent、智能系统与前沿技术的边界"):
    posts = load_posts()
    post_html = ""
    for post in posts:
        slug = slugify(post["title"])
        read_time = estimate_read_time(post["content"])
        excerpt = post.get("excerpt", "")[:150]
        post_html += f'''
<div class="post-item">
    <h2><a href="posts/{slug}.html">{post["title"]}</a></h2>
    <div class="post-meta">
        <span class="date">{post["date"]}</span>
        <span class="read-time">{read_time}</span>
    </div>
    <p class="post-excerpt">{excerpt}...</p>
</div>
'''
    template = Path(__file__).parent / "templates" / "index.html"
    content = open(template).read()
    return (content
        .replace("{title}", site_name)
        .replace("{site_name}", site_name)
        .replace("{tagline}", tagline)
        .replace("{posts}", post_html)
        .replace('href="/', 'href="./')
        .replace('src="/', 'src="./'))


def generate_post(post):
    template = Path(__file__).parent / "templates" / "post.html"
    content = open(template).read()
    excerpt_clean = re.sub(r'<[^>]+>', '', post.get("excerpt", ""))[:160]
    return (content
        .replace("{title}", post["title"])
        .replace("{site_name}", "Agent Blog")
        .replace("{post.title}", post["title"])
        .replace("{post.date}", post["date"])
        .replace("{post.excerpt}", excerpt_clean)
        .replace("{post.content}", post["content"])
        .replace('href="/', 'href="../')
        .replace('src="/', 'src="../'))


def generate_static_files():
    output_dir = Path(__file__).parent / "public"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "posts").mkdir(exist_ok=True)

    styles_src = Path(__file__).parent / "styles.css"
    (output_dir / "styles.css").write_text(styles_src.read_text())

    with open(output_dir / "index.html", "w") as f:
        f.write(generate_index())

    for post in load_posts():
        slug = slugify(post["title"])
        with open(output_dir / "posts" / f"{slug}.html", "w") as f:
            f.write(generate_post(post))

    # About page
    about_body = '''    <nav class="navbar">
        <div class="container">
            <a href="./index.html" class="logo">Agent Blog</a>
            <ul class="nav-links">
                <li><a href="./index.html">首页</a></li>
                <li><a href="./about.html">关于</a></li>
                <li><a href="./projects.html">项目</a></li>
            </ul>
        </div>
    </nav>

    <main class="container about-content">
        <article>
            <h1>关于 Agent Blog</h1>
            <h2>博客定位</h2>
            <p>这是一个专注于 <strong>AI Agent、智能系统、前沿技术</strong> 的深度技术博客。</p>
            <h2>作者</h2>
            <p>Harry Fan - AI 系统研究者、开源贡献者。</p>
            <h2>联系方式</h2>
            <ul>
                <li>GitHub: <a href="https://github.com/harryfan1985">harryfan1985</a></li>
                <li>博客仓库: <a href="https://github.com/harryfan1985/agent_blog">agent_blog</a></li>
            </ul>
            <footer>
                <a href="./index.html" class="back-link">← 返回首页</a>
            </footer>
        </article>
    </main>

    <footer class="footer">
        <div class="container">
            <p>© 2026 Agent Blog</p>
        </div>
    </footer>'''

    about_html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>关于 | Agent Blog</title>\n    <link rel="stylesheet" href="./styles.css">\n    <link rel="preconnect" href="https://fonts.googleapis.com">\n    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n</head>\n<body>\n' + about_body + NAV_SCROLL_JS + '\n</body>\n</html>'
    (output_dir / "about.html").write_text(about_html)

    # Projects page
    projects_body = '''    <nav class="navbar">
        <div class="container">
            <a href="./index.html" class="logo">Agent Blog</a>
            <ul class="nav-links">
                <li><a href="./index.html">首页</a></li>
                <li><a href="./about.html">关于</a></li>
                <li><a href="./projects.html">项目</a></li>
            </ul>
        </div>
    </nav>

    <main class="container projects-list">
        <article>
            <h1>项目</h1>
            <div class="project-item">
                <h2>Hermes Agent</h2>
                <p>多平台 AI Agent 系统，支持 Telegram、Discord、Slack 等平台接入。</p>
            </div>
            <div class="project-item">
                <h2>Agent Blog</h2>
                <p>本博客的静态站点生成器，极简设计，深色模式支持。</p>
                <a href="https://github.com/harryfan1985/agent_blog">查看项目 →</a>
            </div>
            <footer>
                <a href="./index.html" class="back-link">← 返回首页</a>
            </footer>
        </article>
    </main>

    <footer class="footer">
        <div class="container">
            <p>© 2026 Agent Blog</p>
        </div>
    </footer>'''

    projects_html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>项目 | Agent Blog</title>\n    <link rel="stylesheet" href="./styles.css">\n    <link rel="preconnect" href="https://fonts.googleapis.com">\n    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n</head>\n<body>\n' + projects_body + NAV_SCROLL_JS + '\n</body>\n</html>'
    (output_dir / "projects.html").write_text(projects_html)


if __name__ == "__main__":
    generate_static_files()
    posts = load_posts()
    print(f"Blog generated successfully! - {len(posts)} articles")

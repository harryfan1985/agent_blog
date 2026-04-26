#!/usr/bin/env python3
"""Modern static blog generator with enhanced features."""

import yaml
import re
from pathlib import Path
from datetime import datetime


def load_posts():
    """Load posts from YAML file."""
    data_path = Path(__file__).parent / "data" / "posts.yaml"
    with open(data_path, "r") as f:
        posts = yaml.safe_load(f)["posts"]
    
    # Normalize posts: ensure all have title, date, excerpt
    for post in posts:
        if "title" not in post:
            content = post.get("content", "")
            match = re.search(r'<h1>([^<]+)</h1>', content)
            if match:
                post["title"] = match.group(1)
            else:
                post["title"] = "Untitled"
        
        if "date" not in post:
            match = re.search(r'发布日期[：:]\s*([^<\n]+)', content)
            if match:
                post["date"] = match.group(1).strip()
            else:
                post["date"] = "Unknown"
        
        if "excerpt" not in post:
            content = post.get("content", "")
            # Remove HTML tags for excerpt
            text = re.sub(r'<[^>]+>', '', content)
            post["excerpt"] = text[:200].strip()
    
    return posts


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\\s]', '-', slug)
    slug = slug.replace(' ', '-')
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def estimate_read_time(content):
    """Estimate reading time in minutes (200 words/min for Chinese)."""
    text = re.sub(r'<[^>]+>', '', content)
    # Chinese characters count
    chinese_chars = len(re.findall(r'[\\u4e00-\\u9fff]', text))
    # English words
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    total = chinese_chars + english_words
    minutes = max(1, round(total / 400))
    return f"{minutes} 分钟阅读"


def generate_index(site_name="Agent Blog", tagline="探索 AI Agent、智能系统与前沿技术的边界"):
    """Generate the index page with enhanced layout."""
    posts = load_posts()
    
    post_html = ""
    for post in posts:
        slug = slugify(post["title"])
        read_time = estimate_read_time(post["content"])
        excerpt = post.get("excerpt", "")
        if len(excerpt) > 150:
            excerpt = excerpt[:150] + "..."
        
        post_html += f'''
<div class="post-item">
    <h2><a href="posts/{slug}.html">{post["title"]}</a></h2>
    <div class="post-meta">
        <span class="date">{post["date"]}</span>
        <span class="read-time">{read_time}</span>
    </div>
    <p class="post-excerpt">{excerpt}</p>
</div>
'''
    
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
    
    excerpt = post.get("excerpt", "")
    excerpt_clean = re.sub(r'<[^>]+>', '', excerpt)[:160]
    
    return (
        content.replace("{title}", post["title"])
        .replace("{site_name}", "Agent Blog")
        .replace("{post.title}", post["title"])
        .replace("{post.date}", post["date"])
        .replace("{post.excerpt}", excerpt_clean)
        .replace("{post.content}", post["content"])
        .replace('href="/', 'href="../')
        .replace('src="/', 'src="../')
    )


def generate_static_files():
    """Generate all static HTML files."""
    output_dir = Path(__file__).parent / "public"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "posts").mkdir(exist_ok=True)
    
    # Copy styles
    styles_src = Path(__file__).parent / "styles.css"
    styles_dst = output_dir / "styles.css"
    styles_dst.write_text(styles_src.read_text())
    
    # Generate index
    with open(output_dir / "index.html", "w") as f:
        f.write(generate_index())
    
    # Generate each post
    for post in load_posts():
        slug = slugify(post["title"])
        with open(output_dir / "posts" / f"{slug}.html", "w") as f:
            f.write(generate_post(post))
    
    # Generate about page
    (output_dir / "about.html").write_text('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>关于 | Agent Blog</title>
    <meta name="description" content="关于 Agent Blog 技术博客">
    <link rel="stylesheet" href="./styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
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
            <p>这是一个专注于 <strong>AI Agent、智能系统、前沿技术</strong> 的深度技术博客。内容包括：</p>
            <ul>
                <li>开源 AI 项目深度分析与架构解读</li>
                <li>多 Agent 系统设计与实现经验</li>
                <li>本地 LLM 部署与优化实践</li>
                <li>技术趋势与行业洞察</li>
            </ul>
            
            <h2>作者</h2>
            <p>Harry Fan — AI 系统研究者、开源贡献者。专注于构建可落地的智能系统，探索 Agent 编排与自主决策的边界。</p>
            
            <h2>设计理念</h2>
            <blockquote>
                极简主义、内容为王、无追踪、无干扰。
            </blockquote>
            <p>博客采用纯静态生成，无 JavaScript、无广告、无第三方追踪。所有内容可离线阅读，专注于信息密度与可读性。</p>
            
            <h2>技术栈</h2>
            <table>
                <tr><th>组件</th><th>技术</th></tr>
                <tr><td>生成器</td><td>Python + YAML</td></tr>
                <tr><td>样式</td><td>纯 CSS（深色模式支持）</td></tr>
                <tr><td>托管</td><td>GitHub Pages</td></tr>
                <tr><td>字体</td><td>Inter（Google Fonts）</td></tr>
            </table>
            
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
            <p>© 2026 Agent Blog · 技术博客 · 探索 AI 与智能系统的边界</p>
        </div>
    </footer>
</body>
</html>''')
    
    # Generate projects page
    (output_dir / "projects.html").write_text('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目 | Agent Blog</title>
    <meta name="description" content="Harry Fan 的开源项目与技术实验">
    <link rel="stylesheet" href="./styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
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
                <p>多平台 AI Agent 系统，支持 Telegram、Discord、Slack 等平台接入，具备工具调用、记忆管理、子 Agent 编排能力。</p>
                <p><strong>技术栈</strong>: Python, Anthropic API, OpenAI, SQLite, Asyncio</p>
                <a href="https://github.com/harryfan1985/hermes-agent">查看项目 →</a>
            </div>
            
            <div class="project-item">
                <h2>OpenClaw</h2>
                <p>树莓派上的本地 AI Agent 网关，连接 Telegram Bot 与本地 LLM 服务，实现离线智能对话。</p>
                <p><strong>技术栈</strong>: Raspberry Pi, LMStudio, Telegram Bot API</p>
            </div>
            
            <div class="project-item">
                <h2>Oh My OpenAgent</h2>
                <p>多 Agent 编排框架，实现 Agent 间的协作、任务分发与结果整合。</p>
                <p><strong>技术栈</strong>: Python, OpenCode CLI, Agent Protocol</p>
            </div>
            
            <div class="project-item">
                <h2>Agent Blog</h2>
                <p>本博客的静态站点生成器，极简设计，深色模式支持，无 JavaScript。</p>
                <p><strong>技术栈</strong>: Python, YAML, CSS, GitHub Pages</p>
                <a href="https://github.com/harryfan1985/agent_blog">查看项目 →</a>
            </div>
            
            <footer>
                <a href="./index.html" class="back-link">← 返回首页</a>
            </footer>
        </article>
    </main>

    <footer class="footer">
        <div class="container">
            <p>© 2026 Agent Blog · 技术博客 · 探索 AI 与智能系统的边界</p>
        </div>
    </footer>
</body>
</html>''')


if __name__ == "__main__":
    generate_static_files()
    print("Blog generated successfully!")
    posts = load_posts()
    print(f"  - {len(posts)} articles")
    print("  - Modern theme with dark mode support")
    print("  - Responsive design for mobile/desktop")
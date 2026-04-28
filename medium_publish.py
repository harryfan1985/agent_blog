#!/usr/bin/env python3
"""
Medium 文章发布脚本
从 agent_blog data/posts.yaml 读取文章，发布到 Medium

使用方法:
    python3 medium_publish.py --post-id <文章ID或索引> [--status draft|public|unlisted]
    python3 medium_publish.py --list                          # 列出可发布的文章
    python3 medium_publish.py --latest                        # 发布最新文章

配置:
    在脚本同级目录创建 .env 文件，内容:
    MEDIUM_INTEGRATION_TOKEN=你的token
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

# 配置
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
POSTS_YAML = SCRIPT_DIR / "data" / "posts.yaml"
MEDIUM_API_BASE = "https://api.medium.com/v1"


def load_env():
    """从 .env 文件加载环境变量"""
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def get_token():
    """获取 Medium integration token"""
    token = os.environ.get("MEDIUM_INTEGRATION_TOKEN")
    if not token:
        print("❌ 错误: 未找到 MEDIUM_INTEGRATION_TOKEN")
        print(f"   请在 {ENV_FILE} 文件中添加:")
        print("   MEDIUM_INTEGRATION_TOKEN=你的token")
        print("   获取地址: https://medium.com/me/settings")
        sys.exit(1)
    return token


def api_request(method, endpoint, token, data=None):
    """调用 Medium API"""
    import urllib.request
    import urllib.error

    url = f"{MEDIUM_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"❌ API 错误: {e.code} {e.reason}")
        print(f"   响应: {error_body}")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def get_user_info(token):
    """获取 Medium 用户信息"""
    result = api_request("GET", "/me", token)
    if result and "data" in result:
        return result["data"]
    return None


def html_to_markdown(html_content):
    """将博客 HTML 内容转换为 Markdown"""
    md = html_content

    # 移除 <br> 标签
    md = re.sub(r"<br\s*/?>", "\n", md, flags=re.IGNORECASE)

    # 标题转换
    md = re.sub(r"<h1[^>]*>(.*?)</h1>", r"# \1", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<h2[^>]*>(.*?)</h2>", r"## \1", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<h3[^>]*>(.*?)</h3>", r"### \1", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<h4[^>]*>(.*?)</h4>", r"#### \1", md, flags=re.IGNORECASE | re.DOTALL)

    # 段落
    md = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", md, flags=re.IGNORECASE | re.DOTALL)

    # 粗体/斜体
    md = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", md, flags=re.IGNORECASE | re.DOTALL)

    # 代码
    md = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(
        r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        r"```\n\1\n```",
        md,
        flags=re.IGNORECASE | re.DOTALL,
    )
    md = re.sub(r"<pre[^>]*>(.*?)</pre>", r"```\n\1\n```", md, flags=re.IGNORECASE | re.DOTALL)

    # 链接
    md = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", md, flags=re.IGNORECASE | re.DOTALL)

    # 列表
    md = re.sub(r"<ul[^>]*>(.*?)</ul>", r"\1", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<ol[^>]*>(.*?)</ol>", r"\1", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", md, flags=re.IGNORECASE | re.DOTALL)

    # 引用
    md = re.sub(r"<blockquote[^>]*>(.*?)</blockquote>", r"> \1", md, flags=re.IGNORECASE | re.DOTALL)

    # 表格（简化处理）
    md = re.sub(r"<table[^>]*>(.*?)</table>", r"\1", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<tr[^>]*>(.*?)</tr>", r"\1\n", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<th[^>]*>(.*?)</th>", r"| \1 ", md, flags=re.IGNORECASE | re.DOTALL)
    md = re.sub(r"<td[^>]*>(.*?)</td>", r"| \1 ", md, flags=re.IGNORECASE | re.DOTALL)

    # 清理多余标签
    md = re.sub(r"<[^>]+>", "", md)

    # 清理多余空行
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip()


def load_posts():
    """从 posts.yaml 加载文章列表"""
    if not POSTS_YAML.exists():
        print(f"❌ 错误: 找不到 {POSTS_YAML}")
        sys.exit(1)

    with open(POSTS_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("posts", [])


def list_posts(posts):
    """列出所有文章"""
    print(f"\n📄 共 {len(posts)} 篇文章:\n")
    for i, post in enumerate(posts):
        title = post.get("title", "无标题")
        date = post.get("date", "无日期")
        print(f"  [{i}] {title} ({date})")
    print()


def publish_post(post, user_id, token, status="draft"):
    """发布单篇文章到 Medium"""
    title = post.get("title", "无标题")
    content_html = post.get("content", "")

    # 转换 HTML → Markdown
    content_md = html_to_markdown(content_html)

    # 提取标签（从内容中推断）
    tags = []
    if "AI" in content_md or "LLM" in content_md:
        tags.extend(["ai", "llm"])
    if "Agent" in content_md:
        tags.append("ai-agent")
    if "代码" in content_md or "编程" in content_md:
        tags.append("programming")
    if not tags:
        tags = ["technology"]

    # 构建请求
    payload = {
        "title": title,
        "contentFormat": "markdown",
        "content": content_md,
        "tags": tags[:5],  # Medium 最多 5 个标签
        "publishStatus": status,
    }

    # 如果有原始链接，添加 canonicalUrl
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    payload["canonicalUrl"] = f"https://harryfan1985.github.io/agent_blog/posts/{slug}.html"

    print(f"\n📝 发布文章: {title}")
    print(f"   状态: {status}")
    print(f"   标签: {', '.join(tags)}")

    result = api_request("POST", f"/users/{user_id}/posts", token, payload)

    if result and "data" in result:
        data = result["data"]
        print(f"✅ 发布成功!")
        print(f"   Medium URL: {data.get('url', 'N/A')}")
        print(f"   Post ID: {data.get('id', 'N/A')}")
        print(f"   状态: {data.get('publishStatus', 'N/A')}")
        return data
    else:
        print(f"❌ 发布失败")
        return None


def main():
    parser = argparse.ArgumentParser(description="发布 agent_blog 文章到 Medium")
    parser.add_argument("--list", action="store_true", help="列出所有文章")
    parser.add_argument("--latest", action="store_true", help="发布最新文章")
    parser.add_argument("--post-id", type=int, help="发布指定索引的文章 (0=最新)")
    parser.add_argument("--status", choices=["draft", "public", "unlisted"], default="draft",
                        help="发布状态 (默认: draft)")
    parser.add_argument("--canonical", help="自定义 canonical URL")

    args = parser.parse_args()

    # 加载环境变量
    load_env()

    # 加载文章
    posts = load_posts()
    if not posts:
        print("❌ 错误: 没有找到文章")
        sys.exit(1)

    # 列出文章
    if args.list:
        list_posts(posts)
        return

    # 确定要发布的文章
    if args.latest:
        post = posts[0]
    elif args.post_id is not None:
        if args.post_id < 0 or args.post_id >= len(posts):
            print(f"❌ 错误: 索引 {args.post_id} 超出范围 (0-{len(posts)-1})")
            sys.exit(1)
        post = posts[args.post_id]
    else:
        print("❌ 错误: 请指定 --latest, --post-id 或 --list")
        parser.print_help()
        sys.exit(1)

    # 获取 token 和用户信息
    token = get_token()
    user = get_user_info(token)
    if not user:
        print("❌ 错误: 无法获取 Medium 用户信息，请检查 token 是否有效")
        sys.exit(1)

    print(f"👤 Medium 用户: {user.get('name', 'Unknown')} (@{user.get('username', 'Unknown')})")

    # 发布
    result = publish_post(post, user["id"], token, args.status)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

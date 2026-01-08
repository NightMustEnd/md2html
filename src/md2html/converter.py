"""Markdown to HTML conversion logic."""

import json
import re
import shutil
from importlib import resources
from pathlib import Path

from markdown import Markdown
from pygments.formatters import HtmlFormatter

# HTMLテンプレート
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ドキュメント</title>
    <link rel="stylesheet" href="assets/style.css">
    <style>{pygments_css}</style>
</head>
<body>
    <div class="container">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h1>ドキュメント</h1>
                <button class="sidebar-toggle" id="sidebarToggle" aria-label="サイドバーを閉じる">×</button>
            </div>
            <nav class="nav-menu">
                <a href="index.html" class="nav-item">ホーム</a>
{nav_items}
            </nav>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="検索...">
                <div id="searchResults" class="search-results"></div>
            </div>
            <div class="theme-toggle">
                <button id="themeToggle" aria-label="テーマ切替">🌙</button>
            </div>
        </aside>
        <main class="main-content">
            <button class="sidebar-open-btn" id="sidebarOpenBtn" aria-label="サイドバーを開く">☰</button>
            <article class="content">
                {content}
            </article>
            <aside class="toc" id="toc">
                <h2>目次</h2>
                {toc_html}
            </aside>
        </main>
    </div>
    <script src="assets/search-index.js"></script>
    <script src="assets/app.js"></script>
</body>
</html>"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ドキュメント</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h1>ドキュメント</h1>
                <button class="sidebar-toggle" id="sidebarToggle" aria-label="サイドバーを閉じる">×</button>
            </div>
            <nav class="nav-menu">
                <a href="index.html" class="nav-item active">ホーム</a>
{nav_items}
            </nav>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="検索...">
                <div id="searchResults" class="search-results"></div>
            </div>
            <div class="theme-toggle">
                <button id="themeToggle" aria-label="テーマ切替">🌙</button>
            </div>
        </aside>
        <main class="main-content">
            <button class="sidebar-open-btn" id="sidebarOpenBtn" aria-label="サイドバーを開く">☰</button>
            <article class="content">
                <h1>ドキュメント一覧</h1>
                <p>Markdownから生成されたドキュメント集です。</p>

                <h2>ページ一覧</h2>
                <div class="doc-list">
{doc_list}
                </div>

                <h2>使い方</h2>
                <p>左サイドバーから各ドキュメントにアクセスできます。検索機能でキーワードを検索したり、ダークモードに切り替えたりできます。</p>
            </article>
        </main>
    </div>
    <script src="assets/search-index.js"></script>
    <script src="assets/app.js"></script>
</body>
</html>"""


def extract_title(md_path: Path) -> str:
    """Markdownファイルから最初の#見出しをタイトルとして抽出"""
    content = md_path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return md_path.stem.replace("-", " ").replace("_", " ").title()


def discover_md_files(source_dir: Path) -> list[tuple[str, str]]:
    """ディレクトリ内の.mdファイルを検出してリストを返す"""
    md_files = []
    for md_path in sorted(source_dir.glob("*.md")):
        title = extract_title(md_path)
        md_files.append((md_path.name, title))
    return md_files


def setup_directories(output_dir: Path) -> None:
    """出力ディレクトリを作成"""
    output_dir.mkdir(exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    # パッケージ内のアセットをコピー
    assets_pkg = resources.files("md2html") / "assets"
    for asset_file in ["style.css", "app.js"]:
        src = assets_pkg / asset_file
        dst = assets_dir / asset_file
        with resources.as_file(src) as src_path:
            shutil.copy(src_path, dst)


def extract_text_from_html(html: str) -> str:
    """HTMLからテキストを抽出（検索インデックス用）"""
    text = re.sub(r"<[^>]+>", "", html)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    return text.strip()


def convert_markdown_to_html(md_path: Path) -> tuple[str, str]:
    """MarkdownをHTMLに変換"""
    md_content = md_path.read_text(encoding="utf-8")

    # リンクを書き換え (.md -> .html)
    md_content = re.sub(
        r"\[([^\]]+)\]\(([^)]+\.md)(#[^)]+)?\)",
        lambda m: f'[{m.group(1)}]({m.group(2).replace(".md", ".html")}{m.group(3) or ""})',
        md_content,
    )

    # Markdown拡張を設定
    md = Markdown(
        extensions=[
            "tables",
            "toc",
            "attr_list",
            "codehilite",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
                "noclasses": False,
            }
        },
    )

    html_content = md.convert(md_content)

    # コードブロックにコピーボタンを追加
    html_content = re.sub(
        r'<div class="highlight"><pre><code>(.*?)</code></pre></div>',
        lambda m: f'<div class="code-block-wrapper"><button class="copy-btn" onclick="copyCode(this)" aria-label="コードをコピー">Copy</button><div class="highlight"><pre><code>{m.group(1)}</code></pre></div></div>',
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r'<div class="highlight"><pre><span></span><code>(.*?)</code></pre></div>',
        lambda m: f'<div class="code-block-wrapper"><button class="copy-btn" onclick="copyCode(this)" aria-label="コードをコピー">Copy</button><div class="highlight"><pre><span></span><code>{m.group(1)}</code></pre></div></div>',
        html_content,
        flags=re.DOTALL,
    )

    # 見出しにアンカーリンクを追加
    html_content = re.sub(
        r'<h([1-6])([^>]*)id="([^"]+)"([^>]*)>(.*?)</h\1>',
        r'<h\1\2id="\3"\4><a href="#\3" class="anchor">#</a>\5</h\1>',
        html_content,
    )

    toc_html = md.toc if hasattr(md, "toc") else ""
    return html_content, toc_html


def generate_nav_items(
    md_files: list[tuple[str, str]], current_file: str | None = None
) -> str:
    """ナビゲーションメニューを生成"""
    nav_items = []
    for md_file, title in md_files:
        html_file = md_file.replace(".md", ".html")
        active = "active" if current_file == html_file else ""
        nav_items.append(
            f'                <a href="{html_file}" class="nav-item {active}">{title}</a>'
        )
    return "\n".join(nav_items)


def generate_doc_list(md_files: list[tuple[str, str]]) -> str:
    """ドキュメント一覧を生成"""
    doc_items = []
    for md_file, title in md_files:
        html_file = md_file.replace(".md", ".html")
        doc_items.append(
            f'                    <div class="doc-card"><a href="{html_file}"><h3>{title}</h3></a></div>'
        )
    return "\n".join(doc_items)


def build_pages(
    source_dir: Path, output_dir: Path, md_files: list[tuple[str, str]]
) -> list[dict]:
    """全ページをビルド"""
    search_index = []

    formatter = HtmlFormatter(style="github-dark")
    pygments_css = formatter.get_style_defs(".highlight")

    for md_file, title in md_files:
        md_path = source_dir / md_file
        if not md_path.exists():
            print(f"警告: {md_file} が見つかりません")
            continue

        html_content, toc_html = convert_markdown_to_html(md_path)

        text_content = extract_text_from_html(html_content)
        html_file = md_file.replace(".md", ".html")
        search_index.append(
            {"title": title, "url": html_file, "content": text_content[:500]}
        )

        nav_items = generate_nav_items(md_files, html_file)
        html = HTML_TEMPLATE.format(
            title=title,
            content=html_content,
            toc_html=toc_html,
            nav_items=nav_items,
            pygments_css=pygments_css,
        )

        output_path = output_dir / html_file
        output_path.write_text(html, encoding="utf-8")
        print(f"生成: {html_file}")

    # インデックスページを生成
    nav_items = generate_nav_items(md_files)
    doc_list = generate_doc_list(md_files)
    index_html = INDEX_TEMPLATE.format(nav_items=nav_items, doc_list=doc_list)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    print("生成: index.html")

    return search_index


def generate_search_index(search_index: list[dict], output_dir: Path) -> None:
    """検索インデックスをJSファイルとして生成"""
    assets_dir = output_dir / "assets"
    js_content = f"window.__SEARCH_INDEX__ = {json.dumps(search_index, ensure_ascii=False, indent=2)};"
    (assets_dir / "search-index.js").write_text(js_content, encoding="utf-8")
    print("生成: assets/search-index.js")

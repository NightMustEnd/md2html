"""Markdown to HTML conversion logic."""

import json
import re
import shutil
from importlib import resources
from pathlib import Path

from markdown import Markdown
from pygments.formatters import HtmlFormatter
from markdownify import MarkdownConverter
from bs4 import BeautifulSoup

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


# ========== HTML to Markdown Conversion ==========


class CustomMarkdownConverter(MarkdownConverter):
    """カスタムMarkdown変換器: コード言語、見出しID、テーブルを保持"""

    def __init__(self, **options):
        # コード言語検出コールバックを設定
        options["code_language_callback"] = self.extract_code_language
        options["heading_style"] = "ATX"  # # スタイルの見出し
        options["bullets"] = "-"  # リストは - を使用
        super().__init__(**options)

    def extract_code_language(self, el):
        """コードブロックのクラスから言語を抽出"""
        # class="highlight-python" や class="language-python" を探す
        classes = el.get("class", [])
        for cls in classes:
            if cls.startswith("highlight-"):
                return cls.replace("highlight-", "")
            if cls.startswith("language-"):
                return cls.replace("language-", "")

        # Pygmentsは <div class="highlight"><pre><code class="language-python"> を使用
        # 親要素と子要素をチェック
        if el.name == "div" and "highlight" in classes:
            pre = el.find("pre")
            if pre:
                code = pre.find("code")
                if code:
                    code_classes = code.get("class", [])
                    for c in code_classes:
                        if c.startswith("language-"):
                            return c.replace("language-", "")
        return None

    def convert_h1(self, el, text, parent_tags=None):
        """h1を変換してID属性を保持"""
        return self._convert_heading(el, text, 1)

    def convert_h2(self, el, text, parent_tags=None):
        """h2を変換してID属性を保持"""
        return self._convert_heading(el, text, 2)

    def convert_h3(self, el, text, parent_tags=None):
        """h3を変換してID属性を保持"""
        return self._convert_heading(el, text, 3)

    def convert_h4(self, el, text, parent_tags=None):
        """h4を変換してID属性を保持"""
        return self._convert_heading(el, text, 4)

    def convert_h5(self, el, text, parent_tags=None):
        """h5を変換してID属性を保持"""
        return self._convert_heading(el, text, 5)

    def convert_h6(self, el, text, parent_tags=None):
        """h6を変換してID属性を保持"""
        return self._convert_heading(el, text, 6)

    def _convert_heading(self, el, text, level):
        """見出しをID保持で変換するヘルパー"""
        heading_id = el.get("id")
        # アンカーリンクをテキストから除去
        # md2htmlは <a href="#id" class="anchor">#</a> を追加
        # これはmarkdownifyでは [#](#id) として変換される
        clean_text = re.sub(r"\[#\]\(#[^\)]+\)\s*", "", text).strip()
        clean_text = re.sub(r"#\s*$", "", clean_text).strip()

        prefix = "#" * level
        if heading_id:
            # attr_list拡張構文を使用: ## Heading {#custom-id}
            return f"\n{prefix} {clean_text} {{#{heading_id}}}\n\n"
        else:
            return f"\n{prefix} {clean_text}\n\n"


def discover_html_files(source_dir: Path) -> list[str]:
    """ディレクトリ内の.htmlファイルを検出してリストを返す"""
    html_files = []
    for html_path in sorted(source_dir.glob("*.html")):
        # index.htmlはスキップ（自動生成されたページ）
        if html_path.name == "index.html":
            continue
        html_files.append(html_path.name)
    return html_files


def extract_html_content(html_full: str) -> str:
    """完全なHTMLページからメインコンテンツを抽出"""
    soup = BeautifulSoup(html_full, "html.parser")

    # md2html固有のコンテンツ構造を探す
    article = soup.find("article", class_="content")
    if article:
        return str(article)

    # フォールバック: 一般的なarticleタグ
    article = soup.find("article")
    if article:
        return str(article)

    # フォールバック: mainタグ
    main = soup.find("main")
    if main:
        # mainにarticleが含まれている場合はそれを使用
        article = main.find("article")
        if article:
            return str(article)
        return str(main)

    # 最後の手段: bodyコンテンツ
    body = soup.find("body")
    if body:
        return str(body)

    # 全て失敗した場合は全体を返す
    return html_full


def convert_html_to_markdown_content(html_content: str, base_filename: str) -> str:
    """HTMLコンテンツをMarkdownに変換してポストプロセス"""
    # カスタム変換器を初期化
    converter = CustomMarkdownConverter(
        heading_style="ATX",
        bullets="-",
        strip=["script", "style", "button"],  # UI要素を除去
    )

    # HTMLをMarkdownに変換
    markdown_content = converter.convert(html_content)

    # ポストプロセス: リンクを書き換え (.html -> .md)
    markdown_content = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\.html(#[^)]+)?\)",
        lambda m: f'[{m.group(1)}]({m.group(2)}.md{m.group(3) or ""})',
        markdown_content,
    )

    # 余分な空白行をクリーンアップ
    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

    # 末尾の改行を確保
    if not markdown_content.endswith("\n"):
        markdown_content += "\n"

    return markdown_content


def convert_html_to_markdown(
    source_dir: Path, output_dir: Path, html_files: list[str]
) -> None:
    """HTMLファイルをMarkdownに変換"""
    output_dir.mkdir(exist_ok=True)

    for html_file in html_files:
        html_path = source_dir / html_file
        if not html_path.exists():
            print(f"警告: {html_file} が見つかりません")
            continue

        # HTMLファイルを読み込み
        try:
            html_full = html_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"警告: {html_file} のエンコーディングに問題があります")
            continue

        if not html_full.strip():
            print(f"警告: {html_file} は空です")
            continue

        # メインコンテンツを抽出
        html_content = extract_html_content(html_full)

        # Markdownに変換
        md_content = convert_html_to_markdown_content(html_content, html_file)

        # 出力
        md_file = html_file.replace(".html", ".md")
        md_path = output_dir / md_file
        md_path.write_text(md_content, encoding="utf-8")
        print(f"生成: {md_file}")

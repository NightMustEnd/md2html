# md2html

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

MarkdownファイルをHTMLドキュメントサイトに変換するCLIツール。

## 機能

- ディレクトリ内の`.md`ファイルを自動検出
- **HTML→Markdown逆変換**（`-r`オプション）
- ナビゲーションサイドバー
- 全文検索
- ダークモード対応
- 目次（TOC）自動生成
- コードハイライト
- コードコピーボタン
- レスポンシブデザイン

## インストール

```bash
pip install git+https://github.com/NightMustEnd/md2html.git
```

## 使い方

### 対話形式

```bash
md2html
```

実行すると入力/出力ディレクトリを聞かれます。

### コマンドライン引数

```bash
# Markdown → HTML
md2html -i /path/to/markdown -o /path/to/output

# HTML → Markdown（逆変換）
md2html -r -i /path/to/html -o /path/to/markdown
```

### オプション

```
-i, --input    入力ディレクトリ
-o, --output   出力ディレクトリ
-r, --reverse  逆変換モード（HTML→Markdown）
-V, --version  バージョン表示
-h, --help     ヘルプ表示
```

## 出力例

```
入力: /Users/user/docs
出力: /Users/user/site
ファイル数: 5

生成: introduction.html
生成: getting-started.html
生成: api-reference.html
生成: faq.html
生成: changelog.html
生成: index.html
生成: assets/search-index.js

完了！
```

## 貢献

貢献は歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

MIT - 詳細は [LICENSE](LICENSE) を参照

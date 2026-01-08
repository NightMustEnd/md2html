# md2html

MarkdownファイルをHTMLドキュメントサイトに変換するCLIツール。

## 機能

- ディレクトリ内の`.md`ファイルを自動検出
- ナビゲーションサイドバー
- 全文検索
- ダークモード対応
- 目次（TOC）自動生成
- コードハイライト
- コードコピーボタン
- レスポンシブデザイン

## インストール

```bash
pip install git+https://github.com/username/md2html.git
```

## 使い方

### 対話形式

```bash
md2html
```

実行すると入力/出力ディレクトリを聞かれます。

### コマンドライン引数

```bash
md2html -i /path/to/markdown -o /path/to/output
```

### オプション

```
-i, --input    入力ディレクトリ（Markdownファイルの場所）
-o, --output   出力ディレクトリ（HTMLの出力先）
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

## ライセンス

MIT

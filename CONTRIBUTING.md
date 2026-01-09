# 貢献ガイド

md2html への貢献に興味を持っていただきありがとうございます！

## Issue の報告

バグを見つけた場合や機能リクエストがある場合は、GitHub Issue を作成してください。

### バグ報告

以下の情報を含めてください：

- 発生した問題の説明
- 再現手順
- 期待される動作
- 実際の動作
- 環境情報（OS、Python バージョン）

### 機能リクエスト

新機能の提案は歓迎します！以下を明確にしてください：

- 追加したい機能の説明
- その機能が必要な理由・ユースケース

## Pull Request

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/NightMustEnd/md2html.git
cd md2html

# 仮想環境を作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 開発用にインストール
pip install -e .
```

### PR の手順

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

### コードスタイル

- Python コードは PEP 8 に準拠
- 意味のある変数名・関数名を使用
- 必要に応じてコメントを追加

## ライセンス

貢献されたコードは MIT ライセンスの下で公開されます。

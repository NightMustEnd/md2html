"""Command-line interface for md2html."""

import argparse
from pathlib import Path

from .converter import (
    build_pages,
    discover_md_files,
    generate_search_index,
    setup_directories,
)


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        prog="md2html",
        description="MarkdownファイルをHTMLに変換するツール",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="入力ディレクトリ（Markdownファイルの場所）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="出力ディレクトリ（HTMLの出力先）",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="逆変換モード: HTMLをMarkdownに変換",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser.parse_args()


def get_directory_interactive(prompt: str, default: Path | None = None) -> Path:
    """対話形式でディレクトリを取得"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        if not user_input:
            return default
    else:
        user_input = input(f"{prompt}: ").strip()
        if not user_input:
            raise ValueError("ディレクトリを指定してください")
    return Path(user_input).expanduser().resolve()


def main() -> int:
    """メイン処理"""
    args = parse_args()

    # モードに応じたプロンプトを設定
    if args.reverse:
        input_prompt = "入力ディレクトリ（HTMLファイルの場所）"
        output_prompt = "出力ディレクトリ（Markdownの出力先）"
        default_output_dir = "markdown"
    else:
        input_prompt = "入力ディレクトリ（Markdownファイルの場所）"
        output_prompt = "出力ディレクトリ（HTMLの出力先）"
        default_output_dir = "site"

    # 入力ディレクトリの決定
    if args.input:
        source_dir = args.input.expanduser().resolve()
    else:
        source_dir = get_directory_interactive(input_prompt)

    # 出力ディレクトリの決定
    if args.output:
        output_dir = args.output.expanduser().resolve()
    else:
        default_output = source_dir.parent / default_output_dir
        output_dir = get_directory_interactive(output_prompt, default_output)

    # 入力ディレクトリの存在確認
    if not source_dir.exists():
        print(f"エラー: 入力ディレクトリが見つかりません: {source_dir}")
        return 1

    if args.reverse:
        # HTML→Markdown変換
        from .converter import convert_html_to_markdown, discover_html_files

        html_files = discover_html_files(source_dir)
        if not html_files:
            print(f"エラー: HTMLファイルが見つかりません: {source_dir}")
            return 1

        print(f"入力: {source_dir}")
        print(f"出力: {output_dir}")
        print(f"ファイル数: {len(html_files)}")
        print()

        convert_html_to_markdown(source_dir, output_dir, html_files)
        print("\n完了！")
    else:
        # Markdown→HTML変換（既存機能）
        md_files = discover_md_files(source_dir)
        if not md_files:
            print(f"エラー: Markdownファイルが見つかりません: {source_dir}")
            return 1

        print(f"入力: {source_dir}")
        print(f"出力: {output_dir}")
        print(f"ファイル数: {len(md_files)}")
        print()

        setup_directories(output_dir)
        search_index = build_pages(source_dir, output_dir, md_files)
        generate_search_index(search_index, output_dir)
        print("\n完了！")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

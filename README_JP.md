# Everything by mdfind
[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />

macOSのSpotlight検索エンジンを活用した超高速ファイル検索ツール

## 主な特徴

* **瞬時検索:** Spotlightインデックスを活用し、ファイルを一瞬で検索
* **検索モード:** ファイル名検索と内容検索の両方に対応
* **精密フィルター:**
    * ファイルサイズ範囲指定（最小/最大バイト数）
    * 拡張子フィルター（例: `pdf`, `docx`）
    * 大文字小文字の区別
    * 完全一致/部分一致の切り替え
* **検索範囲指定:** 特定フォルダ内に検索範囲を限定可能
* **多彩なプレビュー:**
    * テキストファイル（自動エンコード判定）
    * 画像（JPEG/PNG/GIFアニメ/BMP/WEBP/HEIC）
    * SVG画像（自動スケーリング＆中央表示）
    * 動画（再生コントロール付き）
    * 音声ファイル
* **統合メディアプレイヤー:**
    * 標準コントロール付き再生
    * ポップアウト再生ウィンドウ
    * 連続再生モード
    * 音量調整/ミュート機能
* **ワンタッチ検索:**
    * 大容量ファイル（>50MB）
    * 動画ファイル
    * 音楽ファイル
    * 画像ファイル
    * 圧縮ファイル
    * アプリケーション
* **柔軟な並べ替え:** 名前/サイズ/更新日時/パスでソート可能
* **一括操作:**
    * Shift/⌘キーで複数選択
    * 一括処理（開く/削除/コピー/移動/名前変更）
    * 右クリックメニューから各種操作
* **マルチタブ検索：** 複数の検索を同時実行：
    * 異なる検索クエリ用の独立タブ作成
    * 右クリックでタブ管理：閉じる、他を閉じる、左側/右側を閉じる
    * タブごとに独立した検索結果と設定
    * Chrome風のタブ体験（ドラッグ並び替え、スクロールボタン対応）
* **カスタマイズ:**
    * 6つの美しいテーマから選択：
        * ライト/ダーク（システムデフォルト）
        * Tokyo Night/Tokyo Night Storm（東京ナイト）
        * Chinolor Dark/Chinolor Light（中国伝統色）
    * 選択したテーマに合わせたシステムタイトルバー
    * プレビュー表示切替
    * 検索履歴管理
    * ウィンドウ設定自動保存
* **マルチフォーマット出力:** 複数形式で検索結果をエクスポート：
    * JSON - 構造化データ形式
    * Excel (.xlsx) - 書式付きスプレッドシート
    * HTML - Web対応テーブル形式
    * Markdown - ドキュメント向け形式
    * CSV - 従来のカンマ区切り形式
* **大規模対応:** 段階読み込みで数百万件も軽快処理
* **ドラッグ操作:** 検索結果を直接アプリにドロップ
* **パス操作:** フルパス/ディレクトリ/ファイル名を即時コピー

## インストール手順

1. **動作環境:**
    * Python 3.6以上
    * PyQt6ライブラリ

2. **コード取得:**
    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3. **依存関係インストール:**
    ```bash
    pip install -r requirements.txt
    ```

4. **起動:**
    ```bash
    python everything.py
    ```

## カスタマイズ

* **テーマ設定:** ビューメニューからダークモード切替
* **検索履歴:** 
  - 自動保存（入力補完対応）
  - ヘルプメニューで履歴機能OFF可能
* **プレビュー設定:**
  - プレビュー表示/非表示切替
  - 対応フォーマット: テキスト/画像/動画/アプリ

## アプリ化（任意）

py2appでmacOS用実行ファイル生成:

1. **ツールインストール:**
    ```bash
    pip install py2app
    ```

2. **設定ファイル作成:**
    ```bash
    cat > setup.py << 'EOF'
    from setuptools import setup

    APP = ['everything.py']
    DATA_FILES = [
        ('', ['LICENSE.md', 'README.md']),
    ]
    OPTIONS = {
        'argv_emulation': False,
        'packages': ['PyQt6'],
        'excludes': [],
        'plist': {
            'CFBundleName': 'Everything',
            'CFBundleDisplayName': 'Everything',
            'CFBundleVersion': '1.3.6',
            'CFBundleShortVersionString': '1.3.6',
            'CFBundleIdentifier': 'com.appledragon.everythingbymdfind',
            'LSMinimumSystemVersion': '10.14',
            'NSHighResolutionCapable': True,
        }
    }

    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
    EOF
    ```

3. **ビルド:**
    ```bash
    python setup.py py2app
    ```
    `dist`フォルダにmacOSアプリが生成されます

## 開発参加

バグ報告・機能要望・プルリクエスト大歓迎！

## ライセンス

[MITライセンス](LICENSE.md)のもとで公開

## 開発チーム

Apple Dragon

## 最新バージョン

1.3.6

## クレジット

* PyQt6チームに感謝
* オープンソースコミュニティへの敬意


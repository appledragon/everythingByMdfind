# Everything by mdfind

macOSのSpotlight検索エンジンを活用した超高速ファイル検索ツール

## 主な特徴

Everything by mdfind は macOS ユーザーに包括的で強力なファイル検索体験を提供します。

### 🔍 高速検索エンジン
* **瞬時検索:** Spotlightインデックスを活用し、ファイルを一瞬で検索
* **検索モード:** ファイル名検索と内容検索の両方に対応
* **スマートコンテンツインデックス:** ネイティブSpotlight機能を使用してファイル内容を検索

![メインインターフェース](screenshots/01-main-interface-light.png)
*直感的でクリーンなインターフェースが強力な検索機能を提供*

### 🎛️ 高度な検索制御
* **精密フィルター:**
    * ファイルサイズ範囲指定（最小/最大バイト数）
    * 拡張子フィルター（例: `pdf`, `docx`）
    * 大文字小文字の区別
    * 完全一致/部分一致の切り替え
* **検索範囲指定:** 特定フォルダ内に検索範囲を限定可能

![高度なフィルター](screenshots/05-advanced-filters.png)
*高度なフィルタリングオプションで検索結果を精密に絞り込み*

### 📱 マルチタブインターフェース
* **マルチタブ検索：** 複数の検索を同時実行：
    * 異なる検索クエリ用の独立タブ作成
    * 右クリックでタブ管理：閉じる、他を閉じる、左側/右側を閉じる
    * タブごとに独立した検索結果と設定
    * Chrome風のタブ体験（ドラッグ並び替え、スクロールボタン対応）

![マルチタブインターフェース](screenshots/07-multiple-tabs.png)
*直感的なタブシステムで複数のタスクを並行して実行*

### 👁️ 豊富なプレビューシステム
* **多彩なプレビュー:**
    * テキストファイル（自動エンコード判定）
    * 画像（JPEG/PNG/GIFアニメ/BMP/WEBP/HEIC）
    * SVG画像（自動スケーリング＆中央表示）
    * 動画（再生コントロール付き）
    * 音声ファイル

![画像プレビュー](screenshots/10-preview-panel-image.png)
*アプリ内で画像を直接プレビューし、メタデータ情報を表示*

![動画プレビュー](screenshots/11-preview-panel-video.png)
*フルメディアコントロール付きの内蔵動画プレビュー*

### 🎵 統合メディアプレイヤー
* **統合メディアプレイヤー:**
    * 標準コントロール付き再生
    * ポップアウト再生ウィンドウ
    * 連続再生モード
    * 音量調整/ミュート機能

![メディアプレイヤー](screenshots/12-media-player-integrated.png)
*検索結果に統合された全機能メディアプレイヤー*

### ⚡ クイックアクセスブックマーク
* **ワンタッチ検索:**
    * 大容量ファイル（>50MB）
    * 動画ファイル
    * 音楽ファイル
    * 画像ファイル
    * 圧縮ファイル
    * アプリケーション

![ブックマークメニュー](screenshots/16-bookmarks-menu.png)
*よく検索されるファイルタイプのクイックブックマーク*

### 📊 強力なデータ管理
* **柔軟な並べ替え:** 名前/サイズ/更新日時/パスでソート可能
* **一括操作:**
    * Shift/⌘キーで複数選択
    * 一括処理（開く/削除/コピー/移動/名前変更）
    * 右クリックメニューから各種操作

![複数選択操作](screenshots/15-multi-select.png)
*複数ファイルを選択してバッチ操作を実行*

### 🎨 カスタマイズ可能なインターフェース
* **テーマサポート:** ライト/ダークモード切替で快適な表示環境
* **レイアウト制御:** ワークフローに応じてプレビューパネルの表示/非表示を制御
* **検索履歴:** スマート自動補完と履歴記録管理

![ダークモード](screenshots/02-main-interface-dark.png)
*低照度環境に適した美しいダークテーマ*

### 💼 プロフェッショナル機能
* **データ出力:** CSV形式で検索結果をエクスポート可能
* **大規模対応:** 段階読み込みで数百万件も軽快処理
* **ドラッグ操作:** 検索結果を直接アプリにドロップ
* **パス操作:** フルパス/ディレクトリパス/ファイル名をワンクリックでコピー、視覚的確認付き

![CSV エクスポート](screenshots/20-csv-export.png)
*外部分析とレポート用に検索結果をエクスポート*
* **パス操作:** フルパス/ディレクトリ/ファイル名を即時コピー

## 基本操作

1. 検索バーにキーワード入力
2. （任意）検索フォルダを指定（空欄で全領域検索）
3. 詳細フィルターで条件設定
4. ヘッダーをクリックしてソート切替
5. ビュー → プレビューで内容確認
6. ブックマークから頻出ファイルタイプを即時検索
7. 右クリックでコンテキストメニュー表示
8. ファイルを直接ドラッグして使用
9. メディアファイルは内蔵プレイヤーで再生可能
10. 検索毎に新タブが自動作成され、複数検索を同時実行可能
11. タブを右クリックして管理：タブを閉じる、他を閉じる、左側/右側を閉じる
12. ダークモードで目に優しい夜間作業

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
            'CFBundleVersion': '1.3.3',
            'CFBundleShortVersionString': '1.3.3',
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

1.3.3

## クレジット

* PyQt6チームに感謝
* オープンソースコミュニティへの敬意

![スクリーンショット](https://github.com/user-attachments/assets/2b372510-ece7-44b6-ab4e-5a1898318517)

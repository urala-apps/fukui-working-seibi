# fukui-working-seibi — 働く環境整備補助金・奨励金のお問い合わせチャット

福井県労働政策課「働く環境整備補助金・奨励金 ポータルサイト」（https://fukui-working-seibi.jp/）に
**1行貼るだけ** で動く、お問い合わせチャットです。8つの助成金について、募集要項などの資料をもとに答えます。

```html
<script src="https://urala-apps.github.io/fukui-working-seibi/w.js" data-id="seibi" async></script>
```

しくみは [fukui-saigai-shien](https://github.com/urala-apps/fukui-saigai-shien) と同じです。こちらは独立して動きます（配信元・関数・表は別）。

## 仕組み

```
ポータルサイト ──1行──▶ w.js（このリポジトリの GitHub Pages から配る）
                           │ bots/seibi.json を読む
                           ├─ api が空・つながらない → FAQ から近い答えを選ぶ
                           └─ api あり → Edge Function working-chat → Claude
                                          （利用者が最初に選んだ助成金の資料だけを渡して答える）
```

| ファイル | 中身 |
|---|---|
| `w.js` | 小窓の本体（Shadow DOM。サイトの CSS とぶつからない） |
| `bots/seibi.json` | 設定（名前・色・あいさつ・問い合わせ先・FAQ・置いてよいドメイン・月の上限・8つの助成金 `topics`） |
| `bots/seibi.portal.txt` | ホームページに載っている8つの助成金の概要。いつも AI に渡す |
| `bots/seibi.01.txt`〜`seibi.08.txt` | 助成金ごとの交付要領・支給要綱・マニュアル・チラシ・Q&A・様式。選んだ助成金の分だけ渡す |
| `supabase/functions/working-chat/` | AI で答える Edge Function（Claude Haiku 5.5） |
| `supabase/migrations/` | 月の回数（`working_chat_usage`）、公開しない参考メモ（`working_chat_notes`）、質問と答えの記録（`working_chat_logs`）の表 |
| `tools/` | 資料（PDF・Word・Excel）からテキストを作る道具 |
| `index.html` | 見本のページ |

Supabase は補助金ボットと同じプロジェクト（事務局チャットボット / `cudnabiphusjfoieivsq`）を使い、関数と表を分けています。

## 資料を差し替えるとき

1. 募集要項などの zip を展開し、`tools/fix_names.py <フォルダ>` で日本語のファイル名を直す
2. PDF は `pdftotext -layout`、Word は `pandoc -t plain`、Excel は openpyxl でテキストにし、`<作業フォルダ>/<番号>/txt/` に置く
   （画像だけの PDF は文字が取れないので、書き起こしてテキストにする）
3. `python3 tools/build_kb.py <作業フォルダ> bots` で `bots/seibi.<番号>.txt` を作り直す
4. 受付期間などがホームページで変わったら `bots/seibi.portal.txt` と FAQ も直す

記載例に出てくる架空の連絡先は `build_kb.py` で伏せています。個人名・会社名・電話番号が入った資料（問い合わせの回答集など）はリポジトリに置かず、伏せたうえで `working_chat_notes` 表に入れます。`bot` が `seibi` の行は共通、`seibi.01`〜`seibi.08` の行はその助成金を選んだときだけ AI に渡します。

## 書き方の決まり

- 小窓では **最初にどの助成金かを選んでもらう**。選ぶまでは質問を受け付けない（どれの話かを推し量らない）
- 答えは **資料にはっきり書かれている事実だけ**。推測・一般論で答えず、書かれていなければ「資料に記載がありません」と事務局へ案内する。個別の案件が対象になるかの判断はせず、事務局（電話・メール）へ案内する
- 事務局の電話番号は答えに書かず、画面のボタンに任せる（転送される携帯番号は出さない）
- 小窓には「自動の案内で、最終的な判断は審査による」旨を出す（`notice`）

## AI で答えるようにする

1. Supabase に `supabase/migrations/` を当て、`supabase/functions/working-chat` を verify_jwt なしでデプロイする
2. 環境変数：`ANTHROPIC_API_KEY`（同じプロジェクトに入っているものを使う）。`WORKING_BOTS_BASE` は省略すると `https://urala-apps.github.io/fukui-working-seibi/`
3. GitHub Pages を有効にする（Settings → Pages → main ブランチの / (root)）

## 手元で見る

```sh
python3 -m http.server 8000   # http://localhost:8000/ を開く
```

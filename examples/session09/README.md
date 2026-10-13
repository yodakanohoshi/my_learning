# 第9回 見本

[第9回の資料](../../docs/session09/README.md) の成果物「要件メモ＋ストーリー S-01〜S-04（Issue とその控え）」の見本は [`todo-app-snapshots/session-09/`](../todo-app-snapshots/session-09/) です。第8回の終わりに、`docs/` の2つを足しました（コードは変えていません）。ハンズオンの手順7で、自分の版をコミットしたあと、この2つで置き換えます。

## 第8回から増えたもの

| ファイル | 内容 | ハンズオンの手順 |
| --- | --- | --- |
| `docs/requirements.md` | 要件メモ。目的・背景、業務フロー図、状態遷移図（`TODO`・`DONE`・`OVERDUE`）、非機能要件、制約、対象外、未定 | 3（質問の答え）・4（図）・7 |
| `docs/stories.md` | ユーザーストーリー S-01〜S-04（Issue #8〜#11 に登録した本文の控え）。受け入れ条件 (1)〜(15) と、タスクに分けた見積の幅と根拠 | 5（S-01）・6（見積）・7・8（Issue の番号） |
| `README.md` | ドキュメントの表を追記 | 7 |

Issue・ラベル・マイルストーンはリポジトリに含まれないので、`docs/stories.md` の一覧の表が控えです（Issue #7 はこの PR で閉じるタスク、#8〜#11 はストーリー、PR は #12）。

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-08 session-09
less session-09/docs/requirements.md
less session-09/docs/stories.md
```

- 図（Mermaid）は、VS Code のプレビュー（`Ctrl+Shift+V`。Mermaid を表示できる拡張機能を入れる）か、GitHub に push して見る
- 受け入れ条件の番号 (1)〜(15) は、第11回のテスト名の頭の番号と対応する（`session-11/tests/test_web.py`）
- 状態遷移図の「期限切れ」の条件（期限の当日を含まない）は、第8回のテスト `test_状態は完了と期限と今日で決まる` と同じ

追いつくときは [examples/README.md](../README.md#遅れた人が追いつく方法) の手順で、フォルダ名を `session-09` にします。Issue は自分のリポジトリに登録し直し、番号が `#8`〜`#11` と違えば `docs/stories.md` の一覧の表を直してください。

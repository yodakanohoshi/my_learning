# 第10回 見本

[第10回の資料](../../docs/session10/README.md) の成果物「API・DB設計書＋システム構成図」の見本は [`todo-app-snapshots/session-10/`](../todo-app-snapshots/session-10/) です。第9回の終わりに `docs/design/` の3つを足しました（コードは変えていません）。ハンズオンの手順7で、自分の版と、交換で出た質問の反映をコミットしたあと、この3つで置き換えます。

## 第9回から増えたもの

| ファイル | 内容 | 主な図 | ハンズオンの手順 |
| --- | --- | --- | --- |
| `docs/design/api.md` | エンドポイント（`GET /`・`POST /tasks`・`POST /tasks/{id}/done`）、パラメータ、リクエスト・レスポンス例、ステータスコード、入力チェックとエラーの文言、設計レビューで出た質問と反映先 | シーケンス図（追加・完了） | 2（URL・ステータスコード）・3（入力チェック・シーケンス図）・6（6章の質問）・7 |
| `docs/design/db.md` | `tasks` テーブルの定義、制約、DB に持たず計算で求める値（状態）、並び順 | ER図 | 4・7 |
| `docs/design/architecture.md` | 構成要素、通信経路とポート、ミドルウェアとバージョン、環境変数 `TODO_DB_PATH`、起動のしかた、本番公開の想定 | 構成図 | 5・7 |
| `docs/stories.md` | S-01 の関連の欄に設計書へのリンクを追記 | — | 7 |
| `README.md` | ドキュメントの表に設計書の3行を追記 | — | 7 |

Issue #13 はこの PR（#14）で閉じるタスクです。ストーリーの Issue #8〜#11 は第11回の PR #16 で閉じます。

## 見方

```sh
cd ~/handsoff/examples/todo-app-snapshots
diff -rq session-09 session-10
less session-10/docs/design/api.md
```

- 合格基準は「実装者が質問せずに作れるか」。設計書を交換したときに出た質問は `api.md` の 6章に、反映した場所と一緒に残している
- 入力チェックの文言（`api.md` 4章）は、第9回の受け入れ条件 (3)〜(5)・(14) と一字も違わない
- 書いたとおりに作ったものが第11回（`session-11/`）。`diff -ru session-10 session-11` で、設計書から何が実装になったかを見比べられる

追いつくときは [examples/README.md](../README.md#遅れた人が追いつく方法) の手順で、フォルダ名を `session-10` にします。

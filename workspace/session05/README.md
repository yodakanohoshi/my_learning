# 第5回 作業場所（手順書のリポジトリ）

[第5回の資料](../../docs/session05/README.md) の手順で、このディレクトリを Git のリポジトリにします。第4回の手順書（`workspace/session04/` の `README.md`・`mise.toml` など）をここにコピーして使います。

```sh
cd ~/handsoff/workspace/session05
pwd        # session05 にいることを確かめてから
git init
```

- `git init` するのはこのディレクトリだけです。`~/handsoff` や `workspace/` では実行しないでください
- この案内の `README.md` は、コピーした手順書の `README.md` で上書きしてかまいません
- コピー元の `workspace/session04/` はそのまま残します
- 演習では、ここで Issue → ブランチ → PR → セルフレビュー → マージと、コンフリクトの解決を1人で練習します
- 手順書の改善は、これ以降もこのリポジトリで Issue → ブランチ → PR の流れで入れます。アプリのコードと設計書は、第6回に作る `workspace/todo-app/` で管理します

見本は [examples/session05/](../../examples/session05/README.md) にあります。

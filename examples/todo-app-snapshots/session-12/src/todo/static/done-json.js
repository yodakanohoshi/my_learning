// 比較用: 「完了」だけを JSON の API（API設計書 A-07）で行う版。
// 試すときは templates/base.html の app.js をこのファイルに替える（追加はふつうのフォーム送信になる）。
//
// サーバは {"id": 2, "done": true} を返すだけなので、画面の組み立て（DOM の書き換え）はここで行う。
// app.js と比べると、表示の決まり（状態の文字・class・ボタンを消す）がサーバのテンプレートと
// ここの2か所に分かれ、並べ替えや「期限切れだけ」の表示はここでは直らない。
document.addEventListener("submit", async (event) => {
  const form = event.target;
  const item = form.closest("li.task");
  if (!item) return; // 完了ボタン以外のフォームは、ふつうに送る

  event.preventDefault();
  const id = item.id.replace("task-", "");
  const response = await fetch(`/api/tasks/${id}/done`, { method: "POST" });
  const data = await response.json();

  if (!response.ok) {
    const p = document.createElement("p");
    p.className = "error";
    p.setAttribute("role", "alert");
    // サーバから来た文字列は textContent で入れる。innerHTML に入れると XSS になる
    p.textContent = data.detail;
    document.getElementById("error-area").replaceChildren(p);
    return;
  }
  item.className = "task status-done";
  item.querySelector(".status").textContent = "完了";
  form.remove();
});

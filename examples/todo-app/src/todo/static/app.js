// フォームの送信を横取りして fetch で送り、サーバが返す HTML 断片で画面の一部だけを差し替える。
// 送り先は、フォームの data-fragment 属性に書いてある「HTML 断片を返す URL」（API設計書 A-05・A-06）。
// JavaScript が動かないときは、ふつうのフォーム送信（ページ全体の再表示）のまま動く。
//
// document にまとめてイベントを付けている（イベントの委譲）のは、一覧を差し替えると
// 新しい「完了」ボタンには、個別に付けたイベントが付いていないため。
document.addEventListener("submit", async (event) => {
  const form = event.target;
  const url = form.dataset.fragment;
  if (!url) return; // data-fragment のないフォームは、ふつうに送る

  event.preventDefault(); // ふつうの送信（画面の移動）を止める
  const response = await fetch(url, {
    method: "POST",
    body: new FormData(form), // フォームの中身をそのまま送る
  });
  const html = await response.text(); // 成功でもエラーでも、サーバが返すのは HTML 断片

  const errorArea = document.getElementById("error-area");
  if (response.ok) {
    document.getElementById("task-list").outerHTML = html; // 一覧を丸ごと差し替える
    errorArea.replaceChildren(); // 前のエラーを消す
    if (form.classList.contains("add-form")) form.reset(); // 追加できたら入力欄を空にする
  } else {
    // サーバのテンプレートがエスケープした HTML なので、そのまま入れてよい
    errorArea.innerHTML = html;
  }
});

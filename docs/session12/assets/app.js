// 第12回 手順1の素材（素朴な版）: フォームの送信を横取りして fetch で送り、
// サーバが返す HTML 断片で画面の一部だけを差し替える。
// 送り先は、フォームの data-fragment 属性に書いてある「HTML 断片を返す URL」。
//
// 読み込んだときにあったフォームの1つ1つにイベントを付けている。
// 手順2で、2回目の「完了」がどうなるかを確かめてから、document にまとめて付ける形に直す。
document.querySelectorAll("form[data-fragment]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // ふつうの送信（画面の移動）を止める
    const response = await fetch(form.dataset.fragment, {
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
});

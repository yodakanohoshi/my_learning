// 研修資料の HTML 版だけで動かす（PDF 版には読み込ませない）
// - コードブロックに「コピー」ボタンを付ける
// - ページ下のナビに「戻る」（ブラウザの戻ると同じ）を足す
document.addEventListener("DOMContentLoaded", () => {
  for (const pre of document.querySelectorAll("pre")) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "コピー";
    button.addEventListener("click", async () => {
      const text = (pre.querySelector("code") ?? pre).innerText.replace(/\n$/, "");
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        // file:// などで Clipboard API が使えないとき
        const area = document.createElement("textarea");
        area.value = text;
        document.body.append(area);
        area.select();
        document.execCommand("copy");
        area.remove();
      }
      button.textContent = "コピーしました";
      setTimeout(() => (button.textContent = "コピー"), 1500);
    });
    pre.append(button);
  }

  const nav = document.querySelector(".page-nav");
  if (nav && history.length > 1) {
    const back = document.createElement("button");
    back.type = "button";
    back.textContent = "← 戻る";
    back.addEventListener("click", () => history.back());
    nav.prepend(back);
  }
});

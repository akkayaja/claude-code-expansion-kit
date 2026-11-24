// 연습 사이트 페이지가 열릴 때마다 자동으로 실행되는 코드예요.

// 1) 글 페이지인지 확인: <article>이 있는 페이지만 글 페이지예요.
const article = document.querySelector("article");

if (article) {
  // 2) 본문 = <article> 안의 <p> 문단만 모아요. (제목·날짜는 빼요)
  const paragraphs = article.querySelectorAll("p");
  const text = Array.from(paragraphs, (p) => p.textContent).join("");

  // 3) 띄어쓰기·줄바꿈을 빼고 글자 수를 세요.
  const count = text.replace(/\s/g, "").length;

  // 4) 1분에 500자 기준. 반올림하고, 아무리 짧아도 1분으로 보여 줘요.
  const minutes = Math.max(1, Math.round(count / 500));

  // 5) 안내 상자를 만들어 제목(<h1>) 위, 즉 글의 맨 위에 붙여요.
  const badge = document.createElement("div");
  badge.textContent = `⏱ 읽는 데 약 ${minutes}분 (${count.toLocaleString()}자)`;
  badge.style.cssText =
    "display:inline-block;margin:8px 0;padding:4px 12px;" +
    "background:#fff3bf;border-radius:999px;font-size:14px;color:#333;";
  article.prepend(badge);
}
// 목록 페이지에는 <article>이 없어서 아무 일도 하지 않아요.

// ── 도전: 집중 모드 ──
// 켜면 "← 목록"·날짜 줄을 숨기고, 글씨를 키우고, 종이색 배경으로 바꿔요.
// 켜짐/꺼짐 상태는 이 사이트의 localStorage(사이트별 작은 메모장)에 적어 둬서
// 다른 글로 넘어가도 유지돼요. 그래서 "storage" 권한이 따로 필요 없어요.
const FOCUS_KEY = "rt-focus-mode";

function readFocus() {
  try { return localStorage.getItem(FOCUS_KEY) === "on"; } catch { return false; }
}
function saveFocus(on) {
  try { localStorage.setItem(FOCUS_KEY, on ? "on" : "off"); } catch {}
}
function applyFocus(on) {
  document.documentElement.classList.toggle("rt-focus", on);
}

if (article) {
  const style = document.createElement("style");
  style.textContent = `
    html.rt-focus body { max-width: 640px; font-size: 20px; line-height: 2;
                         background: #fbf8f1; color: #222; }
    html.rt-focus body > a, html.rt-focus .meta { display: none; }
    html.rt-focus article h1 { font-size: 32px; margin-top: 8px; }
    html.rt-focus article p { margin: 0 0 1.3em; }
  `;
  document.head.appendChild(style);
  applyFocus(readFocus()); // 지난번 상태 그대로 시작
}

// ── 미션 4 + 도전: 툴바 버튼(popup)의 부탁에 대답해요 ──
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!article) {
    sendResponse(null); // 글 페이지가 아니면 빈손으로 대답
    return;
  }

  if (message.type === "getArticle") {
    const title = article.querySelector("h1")?.textContent.trim() ?? "";
    // 문단 사이에는 빈 줄을 넣어 AI가 읽기 쉽게 해요.
    const body = Array.from(article.querySelectorAll("p"), (p) => p.textContent.trim()).join("\n\n");
    sendResponse({ title, body, focus: readFocus() });
  }

  if (message.type === "toggleFocus") {
    const on = !readFocus();
    saveFocus(on);
    applyFocus(on);
    sendResponse({ focus: on });
  }
});

// 툴바의 확장 아이콘을 누르면 작은 창(popup)이 열리면서 이 코드가 실행돼요.

const msg = document.getElementById("msg");
const sub = document.getElementById("sub");

// 클립보드에 글자를 넣는 함수. 첫 방법이 막히면 예전 방법으로 한 번 더 시도해요.
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const box = document.createElement("textarea");
    box.value = text;
    document.body.appendChild(box);
    box.select();
    document.execCommand("copy");
    box.remove();
  }
}

async function main() {
  // 1) 지금 보고 있는 탭을 찾아요. (주소나 내용은 보지 않고 번호만 알아내요)
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // 2) 그 탭의 content.js에게 "글 내용 줘"라고 물어봐요.
  let data = null;
  try {
    data = await chrome.tabs.sendMessage(tab.id, { type: "getArticle" });
  } catch {
    data = null; // 연습 사이트가 아니면 content.js가 없어서 대답이 없어요.
  }

  // 3) 글 페이지가 아니면 안내만 하고 끝내요.
  if (!data) {
    msg.textContent = "복사할 글이 없어요";
    sub.textContent = "연습 사이트(localhost:8770)의 글 페이지에서 눌러 주세요.";
    return;
  }

  // 4) AI에게 그대로 붙여 넣을 수 있게 요청 문장 + 제목 + 본문을 묶어요.
  const text = `다음 글을 3줄로 요약해 줘.\n\n제목: ${data.title}\n\n${data.body}`;
  await copyText(text);

  // 5) "복사했어요" 알림
  const chars = data.body.replace(/\s/g, "").length;
  msg.textContent = "✅ 복사했어요";
  sub.textContent = `「${data.title}」 본문 ${chars.toLocaleString()}자. AI 채팅창에 붙여 넣으세요 (⌘V).`;

  // 6) 도전: 집중 모드 버튼. 누를 때마다 켜기 ↔ 끄기
  const button = document.getElementById("focus");
  const showButton = (on) => {
    button.textContent = on ? "🎯 집중 모드 끄기" : "🎯 집중 모드 켜기";
    button.classList.toggle("on", on);
  };
  showButton(data.focus);
  button.style.display = "block";
  button.addEventListener("click", async () => {
    const result = await chrome.tabs.sendMessage(tab.id, { type: "toggleFocus" });
    showButton(result.focus);
  });
}

main();

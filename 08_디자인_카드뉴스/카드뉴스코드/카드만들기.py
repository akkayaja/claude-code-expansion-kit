# 원고 하나로 카드뉴스 PNG 여러 장 만들기
# 사용법: python3 카드뉴스코드/카드만들기.py [원고.md] [저장폴더]
#   (아무것도 안 적으면 결과/카드뉴스_원고.md → 결과/카드/ 로 만들어요)
# 원리: 원고를 '---' 줄에서 자르고 → 장마다 표지/본문/마지막 틀을 골라 빈칸을 채우고
#       → 크롬 '화면 캡처'로 1080x1080 PNG 저장
import html
import subprocess
import sys
from pathlib import Path

폴더 = Path(__file__).resolve().parent.parent          # 08_디자인_카드뉴스
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

원고 = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else 폴더 / "결과/카드뉴스_원고.md"
저장 = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else 폴더 / "결과/카드"
틀 = (폴더 / "카드뉴스코드/카드틀_3종.html").read_text(encoding="utf-8")  # 표지·본문·마지막 3종 틀

# 마지막 장의 '저장' 아이콘 (인스타 저장 버튼 모양을 단순하게 그린 것)
저장아이콘 = ('<svg class="save" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"'
           ' stroke-linejoin="round"><path d="M6 3h12v18l-6-5-6 5z"/></svg>')


def 캡처(html_path, png_path):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1080,1080", f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)


# 1) '---' 줄을 기준으로 카드 나누기 (빈 조각은 버림)
조각들, 지금 = [], []
for 줄 in 원고.read_text(encoding="utf-8").splitlines():
    if 줄.strip() == "---":
        조각들.append(지금)
        지금 = []
    else:
        지금.append(줄)
조각들.append(지금)
카드들 = [[줄 for 줄 in 조각 if 줄.strip()] for 조각 in 조각들]
카드들 = [카드 for 카드 in 카드들 if 카드]

# 2) 장마다 틀에 채워서 HTML → PNG
저장.mkdir(parents=True, exist_ok=True)
전체 = len(카드들)
건너뜀 = 0
for i, 카드 in enumerate(카드들, start=1):
    제목 = 카드[0].lstrip("#").strip()                 # 첫 줄 = 큰 글씨 (# 표시는 지움)
    줄들 = [html.escape(줄) for 줄 in 카드[1:]]

    # 3종 중 고르기: 첫 장 = 표지, 마지막 장 = 마지막, 나머지 = 본문
    종류 = "표지" if i == 1 else "마지막" if i == 전체 else "본문"
    큰숫자 = ""
    if 종류 == "표지":
        if (저장.parent / "표지배경.png").exists():    # 표지 그림이 있으면 배경으로 깔기
            종류 = "표지 그림"
        큰숫자 = '<div class="bar"></div>'
        본문 = f"<p>{'<br>'.join(줄들)}</p>" + '<div class="swipe">옆으로 넘겨 보세요 →</div>'
    elif 종류 == "마지막":
        본문 = f"<p>{'<br>'.join(줄들)}</p>" + 저장아이콘
    else:
        if 제목[:1].isdigit() and "." in 제목:          # "1. 무엇을…" → 큰 숫자 1 + 제목
            숫자, 제목 = 제목.split(".", 1)
            큰숫자 = f'<div class="big">{숫자}</div>'
            제목 = 제목.strip()
        if any("→" in 줄 for 줄 in 줄들):              # 정리 카드: 화살표를 세로 단계로
            단계 = [d.strip() for 줄 in 줄들 for d in 줄.split("→")]
            본문 = '<div class="line"></div>' + "".join(
                f'<span class="step"><b>{n}</b>{d}</span>' for n, d in enumerate(단계, 1))
        else:
            본문 = f'<div class="line"></div><p>{"<br>".join(줄들)}</p>'

    내용 = (틀.replace("{{종류}}", 종류)
              .replace("{{번호}}", f"{i:02d} / {전체:02d}")
              .replace("{{큰숫자}}", 큰숫자)
              .replace("{{제목}}", html.escape(제목))
              .replace("{{본문}}", 본문))
    html_파일 = 저장 / f"카드_{i:02d}.html"
    png_파일 = 저장 / f"카드_{i:02d}.png"

    # 3) 지난번 HTML과 똑같고 PNG도 있으면 건너뛰기 (바뀐 카드만 다시 찍기)
    if png_파일.exists() and html_파일.exists() and html_파일.read_text(encoding="utf-8") == 내용:
        print(f"⏭️  카드_{i:02d}.png  그대로 (안 바뀜)")
        건너뜀 += 1
        continue
    html_파일.write_text(내용, encoding="utf-8")
    캡처(html_파일, png_파일)
    print(f"✅ 카드_{i:02d}.png  [{종류}] {제목}  ← 새로 만듦")

print(f"🎴 {전체}장 중 새로 만든 카드 {전체 - 건너뜀}장, 그대로 둔 카드 {건너뜀}장 → {저장}")

# 도전 미션 1: 같은 배경(bg1)에 문구만 바꾼 A/B 안을 자동으로 10장 만들기
# 사용법: python3 AB10장만들기.py   (결과/ 폴더 안에서 실행)
# 문구 5개 × 스타일 2개(A: 노랑 강조 / B: 민트 강조 + 글씨 아래쪽) = 10장
# 새 그림은 만들지 않아요 → ChatGPT 사용량 0
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "AB10장"
OUT.mkdir(exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BG = "../bg1.png"

# (큰 글씨 1줄, 큰 글씨 2줄(강조), 작은 문구)
문구들 = [
    ("복붙", "끝!",     "엑셀 반복 업무, AI가 대신"),
    ("손", "뗐습니다",  "매주 하던 정리, 이제 자동"),
    ("칼퇴", "성공",    "비개발자의 자동화 3가지"),
    ("말로", "시킨다",  "코딩 없이 AI에게 맡긴 업무"),
    ("야근", "삭제",    "반복 업무 3개를 없앴다"),
]
# A/B 두 스타일: 강조색과 글씨 위치만 다름
스타일 = {
    "A": {"color": "#ffd43b", "top": 110},
    "B": {"color": "#4dd4ac", "top": 200},
}

틀 = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
  html, body {{ margin: 0; width: 1280px; height: 720px; overflow: hidden; }}
  .thumb {{ width: 1280px; height: 720px; position: relative; overflow: hidden;
           background: #222 url("{bg}") center/cover no-repeat;
           font-family: "Apple SD Gothic Neo", sans-serif; }}
  .shade {{ position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0,0,0,.8) 0%, rgba(0,0,0,.35) 50%, transparent 80%); }}
  .big {{ position: absolute; left: 60px; top: {top}px; font-size: 160px; font-weight: 900; color: #fff;
         -webkit-text-stroke: 8px #000; paint-order: stroke fill; line-height: 1.05; letter-spacing: -4px; }}
  .big .hl {{ color: {color}; }}
  .small {{ position: absolute; left: 66px; {small_pos}; font-size: 46px; font-weight: 800; color: #000;
           background: {color}; padding: 8px 22px; border-radius: 10px; }}
</style></head><body>
<div class="thumb"><div class="shade"></div>
  <div class="big">{l1}<br><span class="hl">{l2}</span></div>
  <div class="small">{small}</div>
</div></body></html>"""


def 캡처(html_path, png_path, w, h):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--allow-file-access-from-files", f"--window-size={w},{h}",
                    f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)


파일들 = []
for i, (l1, l2, small) in enumerate(문구들, 1):
    for ab, s in 스타일.items():
        # A는 작은 문구가 아래, B는 위(큰 글씨 위쪽)
        small_pos = "bottom: 80px" if ab == "A" else "top: 90px"
        이름 = f"{i:02d}{ab}_{l1}{l2.replace('!', '')}"
        html = OUT / f"{이름}.html"
        html.write_text(틀.format(bg=BG, top=s["top"], color=s["color"], l1=l1, l2=l2,
                                  small=small, small_pos=small_pos), encoding="utf-8")
        캡처(html, OUT / f"{이름}.png", 1280, 720)
        파일들.append(이름)
        print("✅", 이름 + ".png")

# 10장을 휴대폰 크기(가로 320px)로 5줄 × 2칸 비교판
칸 = "".join(f'<figure><img src="{n}.png"><figcaption>{n}</figcaption></figure>' for n in 파일들)
비교 = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
  body {{ margin: 0; background: #fff; font-family: "Apple SD Gothic Neo", sans-serif; }}
  .grid {{ display: grid; grid-template-columns: repeat(2, 320px); gap: 16px 24px; padding: 20px; }}
  figure {{ margin: 0; }} img {{ width: 320px; height: 180px; border-radius: 8px; display: block; }}
  figcaption {{ margin-top: 4px; font-size: 14px; color: #333; }}
</style></head><body><div class="grid">{칸}</div></body></html>"""
p = OUT / "비교판_10장.html"
p.write_text(비교, encoding="utf-8")
캡처(p, OUT / "비교판_10장.png", 704, 1090)
print("✅ 비교판_10장.png")

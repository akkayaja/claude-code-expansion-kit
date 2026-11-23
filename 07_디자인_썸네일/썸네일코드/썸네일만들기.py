# 썸네일 3안 만들기 + 휴대폰 크기 비교판 만들기
# 사용법: python3 썸네일만들기.py   (결과/ 폴더 안에서 실행)
# 원리: 안마다 HTML(배경 그림 + 글자)을 만들고 → 크롬 '화면 캡처'로 PNG 저장
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 안마다: 파일이름, 배경, 큰 글씨, 작은 문구, 강조색, 왼쪽 그늘(밝은 배경은 그늘 없이)
안들 = [
    ("A", "bg1.png", "복붙<br>끝!",     "엑셀 반복 업무, AI가 대신",  "#ffd43b", True),
    ("B", "bg2.png", "칼퇴<br>성공",    "비개발자의 자동화 3가지",    "#ff6b6b", False),
    ("C", "bg1.png", "말로<br>시킨다",  "코딩 없이 AI에게 맡긴 업무", "#4dd4ac", True),
]

# template/썸네일틀.html 과 같은 틀 (원본은 고치지 않고 여기서 값만 바꿔 씀)
틀 = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
  html, body {{ margin: 0; width: 1280px; height: 720px; overflow: hidden; }}
  .thumb {{ width: 1280px; height: 720px; position: relative; overflow: hidden;
           background: #222 url("{bg}") center/cover no-repeat;
           font-family: "Apple SD Gothic Neo", sans-serif; }}
  .shade {{ position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0,0,0,.8) 0%, rgba(0,0,0,.35) 50%, transparent 80%); }}
  .big {{ position: absolute; left: 60px; top: 110px; font-size: 170px; font-weight: 900; color: #fff;
         -webkit-text-stroke: 8px #000; paint-order: stroke fill; line-height: 1.05; letter-spacing: -4px; }}
  .big .hl {{ color: {color}; }}
  .small {{ position: absolute; left: 66px; bottom: 80px; font-size: 50px; font-weight: 800; color: #000;
           background: {color}; padding: 8px 22px; border-radius: 10px; }}
</style></head><body>
<div class="thumb">{shade}
  <div class="big">{big}</div>
  <div class="small">{small}</div>
</div></body></html>"""


def 캡처(html_path, png_path, w, h):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--allow-file-access-from-files", f"--window-size={w},{h}",
                    f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)


for 이름, bg, big, small, color, 그늘 in 안들:
    줄 = big.split("<br>")
    big_html = 줄[0] + "<br>" + f'<span class="hl">{줄[1]}</span>'  # 둘째 줄은 강조색
    html = HERE / f"썸네일_{이름}.html"
    html.write_text(틀.format(bg=bg, big=big_html, small=small, color=color,
                               shade='<div class="shade"></div>' if 그늘 else ""), encoding="utf-8")
    캡처(html, HERE / f"썸네일_{이름}.png", 1280, 720)
    print("✅", f"썸네일_{이름}.png")

# 휴대폰 화면에서 보이는 크기(가로 약 320px)로 줄여 나란히 놓기
비교 = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
  body { margin: 0; background: #fff; font-family: "Apple SD Gothic Neo", sans-serif; }
  .row { display: flex; gap: 24px; padding: 24px; }
  figure { margin: 0; width: 320px; }
  img { width: 320px; height: 180px; border-radius: 8px; display: block; }
  figcaption { margin-top: 8px; font-size: 15px; color: #333; }
</style></head><body><div class="row">""" + "".join(
    f'<figure><img src="썸네일_{n}.png"><figcaption><b>{n}안</b> · 휴대폰 크기(320px)</figcaption></figure>'
    for n, *_ in 안들) + "</div></body></html>"
p = HERE / "비교판.html"
p.write_text(비교, encoding="utf-8")
캡처(p, HERE / "비교판_휴대폰크기.png", 1056, 250)
print("✅ 비교판_휴대폰크기.png")

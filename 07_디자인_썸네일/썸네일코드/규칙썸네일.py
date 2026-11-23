# 내 채널 썸네일 규칙(CLAUDE.md)대로 썸네일 한 장을 만드는 도구
# 사용법:
#   python3 규칙썸네일.py "큰글씨1줄" "큰글씨2줄" "작은 문구" 배경.png 저장이름.png [--밝은배경]
# 예:
#   python3 규칙썸네일.py "복붙" "끝!" "엑셀 반복 업무, AI가 대신" bg1.png 결과.png
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
강조색 = "#ffd43b"       # 규칙: 노랑
글자영역 = 540            # 규칙: 큰 글씨는 왼쪽 540px(화면의 약 42%) 안에만
최대크기 = 170

if len(sys.argv) < 6:
    print(__doc__ or "사용법은 파일 맨 위 설명을 보세요.")
    sys.exit(1)
l1, l2, small, bg, out = sys.argv[1:6]
밝은배경 = "--밝은배경" in sys.argv

# 규칙: 줄이 길면 글씨를 자동으로 줄여서 그림을 침범하지 않게
# (한글 한 글자 폭 ≈ 글씨 크기 × 0.95)
글자수 = max(len(l1), len(l2))
크기 = min(최대크기, int(글자영역 / (글자수 * 0.95)))

bg_path = Path(bg).resolve()
out_path = Path(out).resolve()
html_path = out_path.with_suffix(".html")
그늘 = "" if 밝은배경 else '<div class="shade"></div>'
# 규칙: 밝은 배경에서는 색을 뒤집는다 (노랑 위에 노랑을 쓰면 묻힘)
if 밝은배경:
    글색, 테두리, 강조글색, 상자색, 상자글색 = "#111", "#fff", "#111", "#111", "#fff"
else:
    글색, 테두리, 강조글색, 상자색, 상자글색 = "#fff", "#000", 강조색, 강조색, "#000"

html_path.write_text(f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
  html, body {{ margin: 0; width: 1280px; height: 720px; overflow: hidden; }}
  .thumb {{ width: 1280px; height: 720px; position: relative; overflow: hidden;
           background: #222 url("{bg_path.as_uri()}") center/cover no-repeat;
           font-family: "Apple SD Gothic Neo", sans-serif; }}
  .shade {{ position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0,0,0,.8) 0%, rgba(0,0,0,.35) 50%, transparent 80%); }}
  .big {{ position: absolute; left: 60px; top: 110px; font-size: {크기}px; font-weight: 900; color: {글색};
         -webkit-text-stroke: 8px {테두리}; paint-order: stroke fill; line-height: 1.05; letter-spacing: -4px; }}
  .big .hl {{ color: {강조글색}; }}
  .small {{ position: absolute; left: 66px; bottom: 80px; font-size: 46px; font-weight: 800; color: {상자글색};
           background: {상자색}; padding: 8px 22px; border-radius: 10px; }}
</style></head><body>
<div class="thumb">{그늘}
  <div class="big">{l1}<br><span class="hl">{l2}</span></div>
  <div class="small">{small}</div>
</div></body></html>""", encoding="utf-8")

subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--allow-file-access-from-files", "--window-size=1280,720",
                f"--screenshot={out_path}", html_path.as_uri()], check=True, capture_output=True)
print(f"✅ {out_path.name} (큰 글씨 {크기}px)")

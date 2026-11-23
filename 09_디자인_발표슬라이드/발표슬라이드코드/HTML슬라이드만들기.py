"""같은 원고(.md)로 브라우저 발표용 HTML 슬라이드 1개 파일을 만든다.

사용법:  uv run python 발표슬라이드코드/HTML슬라이드만들기.py [원고.md] [저장.html] [--캡처]
발표 중 키:  → / 스페이스 = 다음,  ← = 이전,  F = 전체 화면,  N = 대본 보기
--캡처: 장마다 1280×720 PNG 도 저장 (크롬 headless, 설치 불필요)
"""
import html
import subprocess
import sys
from pathlib import Path

from 슬라이드만들기 import 원고읽기   # pptx 코드와 원고 읽는 방법을 같이 씀

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
e = html.escape

CSS = """
:root { --기본:#1E2A3A; --강조:#F28C28; --바탕:#FFFFFF; }
* { box-sizing:border-box; margin:0; }
html,body { height:100%; background:#000; overflow:hidden; }
body { font-family:"Apple SD Gothic Neo",sans-serif; word-break:keep-all; }
#무대 { position:absolute; left:50%; top:50%; width:1280px; height:720px; transform-origin:center; }
.장 { position:absolute; inset:0; padding:67px 86px; background:var(--바탕); color:var(--기본);
      display:none; flex-direction:column; }
.장.보임 { display:flex; }
.장.어둠 { background:var(--기본); color:#fff; }
h1 { font-size:53px; font-weight:800; line-height:1.25; }
.선 { width:115px; height:8px; background:var(--강조); margin:22px 0 48px; }
ul { list-style:none; padding:0; font-size:37px; line-height:1.4; }
li + li { margin-top:22px; }
li::before { content:"• "; }
.큰숫자 { font-size:140px; font-weight:800; color:var(--강조); line-height:1; margin-bottom:36px; }
.쪽 { position:absolute; right:86px; bottom:40px; font-size:19px; opacity:.7; }
/* 표지 */
.표지 { justify-content:center; }
.표지 .선 { margin:0 0 28px; width:154px; height:11px; }
.표지 h1 { font-size:72px; margin-bottom:36px; }
.표지 li::before, .마지막 li::before { content:""; }
/* 단계 */
.단계들 { display:flex; align-items:center; gap:0; margin-top:30px; }
.칸 { flex:1; height:230px; border-radius:22px; background:var(--기본); color:#fff;
      display:flex; flex-direction:column; justify-content:center; text-align:center;
      font-size:37px; font-weight:800; line-height:1.35; padding:0 20px; }
.칸:last-child { background:var(--강조); }
.화살표 { width:72px; text-align:center; font-size:46px; color:var(--기본); }
/* 마지막 */
.마지막 h1 { font-size:64px; margin:40px 0 60px; }
.마지막 li { display:flex; align-items:center; gap:36px; font-size:43px; font-weight:800; }
.마지막 li + li { margin-top:36px; }
.번호 { width:86px; height:86px; border-radius:50%; background:var(--강조); color:var(--기본);
        display:flex; align-items:center; justify-content:center; font-size:43px; }
/* 차트 */
.차트 { flex:1; display:flex; flex-direction:column; }
.범례 { display:flex; gap:36px; justify-content:center; font-size:26px; margin-bottom:10px; }
.범례 i { display:inline-block; width:22px; height:22px; margin-right:10px; vertical-align:-2px; }
.막대판 { flex:1; display:flex; align-items:flex-end; justify-content:space-around;
          border-bottom:3px solid var(--기본); }
.묶음 { display:flex; align-items:flex-end; gap:12px; height:100%; }
.막대 { width:90px; position:relative; transition:height .8s ease; }
.막대 b { position:absolute; top:-40px; left:50%; transform:translateX(-50%);
          font-size:26px; white-space:nowrap; }
.이름표 { display:flex; justify-content:space-around; font-size:31px; padding-top:12px; }
/* 대본 */
#대본 { position:fixed; left:0; right:0; bottom:0; background:rgba(0,0,0,.85); color:#fff;
        font-size:22px; line-height:1.6; padding:18px 40px; display:none; }
#대본.보임 { display:block; }
"""

JS = """
const 장들 = [...document.querySelectorAll('.장')];
let 지금 = Math.max(0, Math.min(장들.length - 1, (parseInt(location.hash.slice(1)) || 1) - 1));
function 보이기() {
  장들.forEach((s, i) => s.classList.toggle('보임', i === 지금));
  document.getElementById('대본').textContent = 장들[지금].dataset.대본 || '(대본 없음)';
  history.replaceState(null, '', '#' + (지금 + 1));
  장들[지금].querySelectorAll('.막대').forEach(m => { m.style.height = '0';
    requestAnimationFrame(() => requestAnimationFrame(() => m.style.height = m.dataset.높이)); });
}
function 맞추기() {
  const 배율 = Math.min(innerWidth / 1280, innerHeight / 720);
  document.getElementById('무대').style.transform = `translate(-50%,-50%) scale(${배율})`;
}
addEventListener('keydown', ev => {
  if (['ArrowRight', ' ', 'PageDown'].includes(ev.key)) 지금 = Math.min(지금 + 1, 장들.length - 1);
  else if (['ArrowLeft', 'PageUp'].includes(ev.key)) 지금 = Math.max(지금 - 1, 0);
  else if (ev.key === 'f' || ev.key === 'F') document.documentElement.requestFullscreen?.();
  else if (ev.key === 'n' || ev.key === 'N') document.getElementById('대본').classList.toggle('보임');
  else return;
  ev.preventDefault(); 보이기();
});
addEventListener('click', () => { 지금 = Math.min(지금 + 1, 장들.length - 1); 보이기(); });
addEventListener('resize', 맞추기);
맞추기(); 보이기();
"""


def 차트html(표):
    머리, *행들 = 표
    최대 = max(float(v) for 행 in 행들 for v in 행[1:])
    색 = ["var(--기본)", "var(--강조)"]
    범례 = "".join(f'<span><i style="background:{색[i]}"></i>{e(n)}</span>' for i, n in enumerate(머리[1:]))
    묶음들 = ""
    for 행 in 행들:
        막대들 = "".join(
            f'<div class="막대" data-높이="{float(v) / 최대 * 88:.1f}%" '
            f'style="height:{float(v) / 최대 * 88:.1f}%;background:{색[i]}"><b>{e(v)}시간</b></div>'
            for i, v in enumerate(행[1:]))
        묶음들 += f'<div class="묶음">{막대들}</div>'
    이름표 = "".join(f"<span>{e(행[0])}</span>" for 행 in 행들)
    return (f'<div class="차트"><div class="범례">{범례}</div>'
            f'<div class="막대판">{묶음들}</div><div class="이름표">{이름표}</div></div>')


def 장html(장, 번호):
    종류, 제목 = 장["종류"], e(장["제목"])
    본문 = 장["본문"][:3]
    대본 = e(" ".join(장["대본"]), quote=True)
    쪽 = f'<div class="쪽">{번호}</div>'
    if 종류 == "표지":
        속 = f'<div class="선"></div><h1>{제목}</h1><ul>' + "".join(f"<li>{e(t)}</li>" for t in 본문) + "</ul>"
        return f'<section class="장 어둠 표지" data-대본="{대본}">{속}</section>'
    if 종류 == "마지막":
        속 = f"<h1>{제목}</h1><ul>" + "".join(
            f'<li><span class="번호">{i}</span>{e(t)}</li>' for i, t in enumerate(본문, 1)) + "</ul>"
        return f'<section class="장 어둠 마지막" data-대본="{대본}">{속}{쪽}</section>'
    머리 = f'<h1>{제목}</h1><div class="선"></div>'
    if 종류 == "단계":
        칸들 = []
        for t in 본문:
            앞, _, 뒤 = t.partition("/" if "/" in t else " ")
            칸들.append(f'<div class="칸">{e(앞)}<br>{e(뒤)}</div>' if 뒤 else f'<div class="칸">{e(t)}</div>')
        속 = '<div class="단계들">' + '<div class="화살표">▶</div>'.join(칸들) + "</div>"
    elif 종류 in ("차트", "표"):
        속 = 차트html(장["표"])
    else:
        속 = (f'<div class="큰숫자">{e(장["큰숫자"])}</div>' if 장["큰숫자"] else "")
        속 += "<ul>" + "".join(f"<li>{e(t)}</li>" for t in 본문) + "</ul>"
    return f'<section class="장" data-대본="{대본}">{머리}{속}{쪽}</section>'


def 만들기(원고, 저장, 캡처=False):
    장들 = 원고읽기(원고)
    몸 = "\n".join(장html(장, i) for i, 장 in enumerate(장들, 1))
    문서 = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(장들[0]["제목"])}</title><style>{CSS}</style></head>'
           f'<body><div id="무대">{몸}</div><div id="대본"></div><script>{JS}</script></body></html>')
    저장 = Path(저장).resolve()
    저장.parent.mkdir(parents=True, exist_ok=True)
    저장.write_text(문서, encoding="utf-8")
    print(f"저장: {저장} ({len(장들)}장, {저장.stat().st_size / 1024:.0f}KB)")
    if 캡처:
        폴더 = 저장.parent / "HTML캡처"
        폴더.mkdir(exist_ok=True)
        for i in range(1, len(장들) + 1):
            png = 폴더 / f"{i:02d}.png"
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--window-size=1280,720", "--virtual-time-budget=2000",
                            f"--screenshot={png}", 저장.as_uri() + f"#{i}"],
                           check=True, capture_output=True)
        print(f"캡처: {폴더} ({len(장들)}장)")


if __name__ == "__main__":
    여기 = Path(__file__).resolve().parent
    인자 = [a for a in sys.argv[1:] if not a.startswith("--")]
    원고 = 인자[0] if 인자 else 여기 / "슬라이드원고.md"
    저장 = 인자[1] if len(인자) > 1 else 여기.parent / "결과" / "업무자동화_제안.html"
    만들기(원고, 저장, 캡처="--캡처" in sys.argv)

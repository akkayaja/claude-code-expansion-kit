"""1인가구 생활비 CSV → A4 세로 인포그래픽 (HTML → PNG·PDF)

숫자는 손으로 적지 않고 전부 CSV에서 계산해서 넣는다.
실행: python3 인포그래픽코드/인포그래픽만들기.py [데이터.csv] [저장폴더]
"""
import csv
import glob
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
남색, 주황 = "#1E2A3A", "#F28C28"
지출항목 = ["주거비", "식비", "교통비", "통신비", "여가비"]
나이대들 = ["20대", "30대", "40대", "50대 이상"]


def 만원(원):
    return 원 / 10000


def 계산(csv경로):
    with open(csv경로, encoding="utf-8-sig") as f:
        행들 = list(csv.DictReader(f))
    n = len(행들)
    평균 = {c: sum(int(r[c]) for r in 행들) / n for c in 지출항목 + ["저축"]}
    지출합 = sum(평균[c] for c in 지출항목)
    나이별여가 = {}
    for a in 나이대들:
        g = [r for r in 행들 if r["나이대"] == a]
        나이별여가[a] = (sum(int(r["여가비"]) for r in g) / len(g), len(g))
    return {
        "사람수": n,
        "평균": 평균,
        "지출합": 지출합,
        "주거비비중": 평균["주거비"] / 지출합,
        "나이별여가": 나이별여가,
        "여가배수": 나이별여가["20대"][0] / 나이별여가["50대 이상"][0],
    }


def 도넛(평균, 지출합):
    """항목별 비율 도넛 (conic-gradient). 주거비만 주황, 나머지는 남색 농도."""
    농도 = {"주거비": 주황, "식비": 남색, "여가비": "#4A5A70", "교통비": "#8A97A8", "통신비": "#C3CBD5"}
    순서 = ["주거비", "식비", "여가비", "교통비", "통신비"]
    조각, 시작 = [], 0.0
    for c in 순서:
        끝 = 시작 + 평균[c] / 지출합 * 100
        조각.append(f"{농도[c]} {시작:.2f}% {끝:.2f}%")
        시작 = 끝
    범례 = "".join(
        f'<li><i style="background:{농도[c]}"></i>{c}<b>{만원(평균[c]):.1f}만</b></li>' for c in 순서
    )
    return f'''<div class="도넛묶음">
      <div class="도넛" style="background:conic-gradient({", ".join(조각)})"><div class="구멍"></div></div>
      <ul class="범례">{범례}</ul></div>'''


def 동전(비중):
    칠할 = round(비중 * 10)
    점 = "".join(f'<span class="동전{" 칠" if i < 칠할 else ""}"></span>' for i in range(10))
    return f'<div class="동전줄">{점}</div><p class="작은설명">지출 10만 원 중 <b>{칠할}만 원</b>이 집값</p>'


def 막대(나이별여가):
    최대 = max(v for v, _ in 나이별여가.values())
    줄 = ""
    for a in 나이대들:
        v, 명 = 나이별여가[a]
        색 = 주황 if a == "20대" else (남색 if a == "50대 이상" else "#8A97A8")
        줄 += f'''<div class="막대줄"><span class="막대이름">{a}<small>{명}명</small></span>
          <span class="막대칸"><span class="막대" style="width:{v / 최대 * 100:.1f}%;background:{색}"></span></span>
          <span class="막대값">{만원(v):.1f}만</span></div>'''
    return f'<div class="막대묶음">{줄}</div>'


CSS = f"""
@page {{ size: A4; margin: 0; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:794px; height:1123px; background:#fff; }}
body {{ font-family:"Apple SD Gothic Neo",sans-serif; color:{남색}; word-break:keep-all;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.쪽 {{ width:794px; height:1123px; display:flex; flex-direction:column; overflow:hidden; }}
header {{ background:{남색}; color:#fff; padding:42px 56px 32px; }}
header .꼬리표 {{ display:inline-block; background:{주황}; color:{남색}; font-weight:800;
                 font-size:15px; padding:5px 12px; border-radius:4px; }}
header h1 {{ font-size:42px; font-weight:900; line-height:1.25; margin-top:14px; }}
header h1 em {{ font-style:normal; color:{주황}; }}
header p {{ font-size:18px; margin-top:12px; opacity:.8; }}
main {{ flex:1; padding:12px 56px 0; display:flex; flex-direction:column; }}
section {{ display:flex; align-items:center; gap:36px; padding:8px 0; border-bottom:2px solid #E6E9EE; flex:1; }}
section:last-child {{ border-bottom:none; }}
.왼쪽 {{ width:270px; flex:none; }}
.번호 {{ font-size:15px; font-weight:800; color:{주황}; display:flex; align-items:center; gap:10px; }}
.번호 img {{ width:58px; height:58px; mix-blend-mode:multiply; }}  /* 그림의 흰 배경을 종이색에 녹임 */
.큰숫자 {{ font-size:74px; font-weight:900; line-height:1.05; margin-top:6px; letter-spacing:-2px; }}
.큰숫자 small {{ font-size:30px; letter-spacing:0; margin-left:4px; }}
.설명 {{ font-size:19px; font-weight:700; margin-top:10px; line-height:1.4; }}
.오른쪽 {{ flex:1; }}
.도넛묶음 {{ display:flex; align-items:center; gap:28px; }}
.도넛 {{ width:170px; height:170px; border-radius:50%; position:relative; flex:none; }}
.구멍 {{ position:absolute; inset:42px; background:#fff; border-radius:50%; }}
.범례 {{ list-style:none; font-size:17px; flex:1; }}
.범례 li {{ display:flex; align-items:center; padding:5px 0; }}
.범례 i {{ width:14px; height:14px; border-radius:3px; margin-right:10px; }}
.범례 b {{ margin-left:auto; }}
.동전줄 {{ display:grid; grid-template-columns:repeat(5,52px); gap:14px; }}
.동전 {{ width:52px; height:52px; border-radius:50%; background:#E6E9EE; }}
.동전.칠 {{ background:{주황}; }}
.작은설명 {{ font-size:18px; margin-top:16px; }}
.작은설명 b {{ color:{주황}; }}
.막대줄 {{ display:flex; align-items:center; gap:12px; margin:9px 0; font-size:17px; }}
.막대이름 {{ width:90px; font-weight:700; }}
.막대이름 small {{ display:block; font-size:12px; font-weight:400; opacity:.6; }}
.막대칸 {{ flex:1; height:26px; background:#F2F4F7; border-radius:4px; }}
.막대 {{ display:block; height:100%; border-radius:4px; }}
.막대값 {{ width:62px; text-align:right; font-weight:800; }}
.결론 {{ background:{주황}; color:{남색}; font-size:22px; font-weight:900; text-align:center;
        padding:18px 40px; margin:4px 56px 0; border-radius:10px; line-height:1.4; }}
footer {{ font-size:13px; color:#6B7683; padding:14px 56px 22px; line-height:1.6; }}
"""


def html만들기(값, 아이콘={}):
    그림 = lambda k: f'<img src="{아이콘[k]}" alt="">' if k in 아이콘 else ''
    평균 = 값["평균"]
    배수 = 값["여가배수"]
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>1인가구 한 달 생활비</title><style>{CSS}</style></head><body><div class="쪽">
<header>
  <span class="꼬리표">1인가구 생활비 인포그래픽</span>
  <h1>혼자 사는 사람,<br>한 달에 <em>얼마</em> 쓸까?</h1>
  <p>{값['사람수']}명에게 물어본 항목별 한 달 생활비</p>
</header>
<main>
  <section>
    <div class="왼쪽"><div class="번호">{그림("지갑")}01 한 달 지출</div>
      <div class="큰숫자">{만원(값['지출합']):.0f}<small>만 원</small></div>
      <div class="설명">저축을 빼고 쓰는 돈<br>(5개 항목 평균의 합)</div></div>
    <div class="오른쪽">{도넛(평균, 값['지출합'])}</div>
  </section>
  <section>
    <div class="왼쪽"><div class="번호">{그림("집")}02 주거비 비중</div>
      <div class="큰숫자">{값['주거비비중'] * 100:.0f}<small>%</small></div>
      <div class="설명">지출에서 가장 큰 몫은<br>집값 (평균 {만원(평균['주거비']):.1f}만 원)</div></div>
    <div class="오른쪽">{동전(값['주거비비중'])}</div>
  </section>
  <section>
    <div class="왼쪽"><div class="번호">{그림("여가")}03 나이별 여가비</div>
      <div class="큰숫자">{배수:.1f}<small>배</small></div>
      <div class="설명">20대는 50대 이상보다<br>여가에 더 많이 써요</div></div>
    <div class="오른쪽">{막대(값['나이별여가'])}</div>
  </section>
</main>
<div class="결론">혼자 살면 생활비 10원 중 4원은 집값,<br>나이가 들수록 여가비는 줄어든다</div>
<footer>출처·기준: 가상 설문 {값['사람수']}명 (연습용 데이터, 실제 통계 아님) · 금액은 1인당 한 달 평균, 만 원 단위 반올림<br>
한 달 지출 = 주거비+식비+교통비+통신비+여가비 평균의 합 · 주거비 비중 = 주거비 ÷ 한 달 지출 · 여가비 배수 = 20대 평균 ÷ 50대 이상 평균</footer>
</div></body></html>"""


def 저장하기(csv경로, 폴더):
    폴더 = Path(폴더).resolve()
    폴더.mkdir(parents=True, exist_ok=True)
    값 = 계산(csv경로)
    html = 폴더 / "1인가구_생활비_인포그래픽.html"
    # 도전①: 결과/아이콘/에 ChatGPT 그림(지갑·집·여가.png)이 있으면 작게 줄인 사본을 만들어 넣는다
    아이콘 = {}
    for 이름 in ["지갑", "집", "여가"]:
        원본 = 폴더 / "아이콘" / f"{이름}.png"
        if 원본.exists():
            작게 = 폴더 / "아이콘" / f"{이름}_작게.png"
            if not 작게.exists():
                # 160px로 줄이고, 거의 흰색(밝기 94% 이상)인 배경은 순수한 흰색으로 바꿔 회색 네모가 안 보이게
                subprocess.run([str(Path.home() / ".local/bin/ffmpeg"), "-y", "-v", "error", "-i", str(원본), "-vf",
                                "scale=160:160,colorlevels=rimax=0.94:gimax=0.94:bimax=0.94", str(작게)],
                               check=True, capture_output=True)
            아이콘[이름] = f"아이콘/{작게.name}"
    html.write_text(html만들기(값, 아이콘), encoding="utf-8")
    png, pdf = html.with_suffix(".png"), html.with_suffix(".pdf")
    공통 = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=2000"]
    subprocess.run(공통 + ["--window-size=794,1123", "--force-device-scale-factor=2",
                         f"--screenshot={png}", html.as_uri()], check=True, capture_output=True)
    subprocess.run(공통 + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", html.as_uri()],
                   check=True, capture_output=True)
    print(f"사람 수 {값['사람수']}명 · 한 달 지출 {만원(값['지출합']):.1f}만 · "
          f"주거비 비중 {값['주거비비중'] * 100:.1f}% · 여가비 배수 {값['여가배수']:.2f}배")
    print(f"저장: {html.name}, {png.name}, {pdf.name} → {폴더}")


if __name__ == "__main__":
    여기 = Path(__file__).resolve().parent
    csv경로 = sys.argv[1] if len(sys.argv) > 1 else glob.glob(str(여기.parent / "data" / "*.csv"))[0]
    폴더 = sys.argv[2] if len(sys.argv) > 2 else 여기.parent / "결과"
    저장하기(csv경로, 폴더)

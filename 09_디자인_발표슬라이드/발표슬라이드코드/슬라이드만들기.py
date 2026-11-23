"""원고(.md)를 읽어 파워포인트(.pptx)를 만든다.

사용법:  uv run python 발표슬라이드코드/슬라이드만들기.py [원고.md] [저장.pptx]

원고 규칙
- 장은 `---` 로 나눈다. 첫 줄 `# 제목` = 그 장의 결론.
- `종류:` 표지 / 본문(생략 가능) / 단계 / 표 / 차트 / 마지막
- `큰숫자:` 값이 있으면 본문 위에 강조색 큰 숫자로 보여 준다.
- `- ` 로 시작하는 줄 = 본문(최대 3줄). `|` 로 시작하는 줄 = 표·차트 데이터.
- 단계 상자 안 줄바꿈 위치는 `/` 로 정한다 (없으면 첫 띄어쓰기).
- `> ` 로 시작하는 줄 = 발표 대본 → 그 장의 '발표자 노트'에 들어간다.
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# ── 디자인 값 (규칙: 색 2가지 = 기본색 + 강조색) ──
기본색 = RGBColor(0x1E, 0x2A, 0x3A)   # 짙은 남색: 글자·도형
강조색 = RGBColor(0xF2, 0x8C, 0x28)   # 주황: 강조 한 곳
흰색 = RGBColor(0xFF, 0xFF, 0xFF)     # 바탕
글꼴 = "Apple SD Gothic Neo"
제목크기, 본문크기 = Pt(40), Pt(28)   # 규칙: 제목 36pt↑, 본문 24pt↑
가로, 세로 = Inches(13.333), Inches(7.5)  # 16:9
여백 = Inches(0.9)


# ── 원고 읽기 ──
def 원고읽기(경로):
    장들 = []
    for 덩어리 in Path(경로).read_text(encoding="utf-8").split("\n---"):
        장 = {"제목": "", "종류": "본문", "큰숫자": None, "본문": [], "표": [], "대본": []}
        for 줄 in 덩어리.strip().splitlines():
            줄 = 줄.strip()
            if 줄.startswith("#"):
                장["제목"] = 줄.lstrip("#").strip()
            elif 줄.startswith("종류:"):
                장["종류"] = 줄.split(":", 1)[1].strip()
            elif 줄.startswith("큰숫자:"):
                장["큰숫자"] = 줄.split(":", 1)[1].strip()
            elif 줄.startswith("- "):
                장["본문"].append(줄[2:].strip())
            elif 줄.startswith("|"):
                장["표"].append([칸.strip() for 칸 in 줄.strip("|").split("|")])
            elif 줄.startswith(">"):
                장["대본"].append(줄.lstrip(">").strip())
        if 장["제목"]:
            장들.append(장)
    return 장들


# ── 작은 도우미들 ──
def 글꼴지정(run, 크기, 색, 굵게=False):
    f = run.font
    f.size, f.bold, f.name = 크기, 굵게, 글꼴
    f.color.rgb = 색
    # 한글은 'ea'(동아시아) 글꼴 칸을 따로 채워야 키노트·파워포인트가 같은 글꼴을 쓴다
    rPr = run._r.get_or_add_rPr()
    for 태그 in ("a:ea", "a:cs"):
        el = rPr.find(qn(태그))
        if el is None:
            el = rPr.makeelement(qn(태그), {})
            rPr.append(el)
        el.set("typeface", 글꼴)


def 글상자(slide, 왼, 위, 너비, 높이, 줄들, 크기, 색, 굵게=False,
         정렬=PP_ALIGN.LEFT, 세로정렬=MSO_ANCHOR.TOP, 줄간격=1.2, 문단사이=Pt(12)):
    tb = slide.shapes.add_textbox(왼, 위, 너비, 높이)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = 세로정렬
    tf.margin_left = tf.margin_right = 0
    for i, 줄 in enumerate(줄들):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = 정렬
        p.line_spacing = 줄간격
        if i:
            p.space_before = 문단사이
        run = p.add_run()
        run.text = 줄
        글꼴지정(run, 크기, 색, 굵게)
    return tb


def 바탕(slide, 색):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = 색


def 도형(slide, 모양, 왼, 위, 너비, 높이, 색):
    s = slide.shapes.add_shape(모양, 왼, 위, 너비, 높이)
    s.fill.solid()
    s.fill.fore_color.rgb = 색
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def 제목달기(slide, 제목):
    글상자(slide, 여백, Inches(0.7), 가로 - 여백 * 2, Inches(1.0),
         [제목], 제목크기, 기본색, 굵게=True, 세로정렬=MSO_ANCHOR.BOTTOM)
    도형(slide, MSO_SHAPE.RECTANGLE, 여백, Inches(1.85), Inches(1.2), Inches(0.08), 강조색)


def 쪽번호(slide, 번호, 색=기본색):
    글상자(slide, 가로 - Inches(1.6), 세로 - Inches(0.7), Inches(1.0), Inches(0.4),
         [str(번호)], Pt(14), 색, 정렬=PP_ALIGN.RIGHT)


# ── 장 종류별 그리기 ──
def 표지(slide, 장):
    바탕(slide, 기본색)
    도형(slide, MSO_SHAPE.RECTANGLE, 여백, Inches(2.3), Inches(1.6), Inches(0.12), 강조색)
    글상자(slide, 여백, Inches(2.7), Inches(11), Inches(1.6),
         [장["제목"]], Pt(54), 흰색, 굵게=True)
    글상자(slide, 여백, Inches(4.4), Inches(11), Inches(1.6),
         장["본문"], 본문크기, 흰색, 문단사이=Pt(6))


def 마지막(slide, 장, 번호):
    바탕(slide, 기본색)
    글상자(slide, 여백, Inches(1.2), Inches(11), Inches(1.2),
         [장["제목"]], Pt(48), 흰색, 굵게=True)
    for i, 줄 in enumerate(장["본문"][:3]):
        위 = Inches(3.0 + i * 1.3)
        동그라미 = 도형(slide, MSO_SHAPE.OVAL, 여백, 위, Inches(0.9), Inches(0.9), 강조색)
        tf = 동그라미.text_frame
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = tf.paragraphs[0].add_run()
        r.text = str(i + 1)
        글꼴지정(r, Pt(32), 기본색, 굵게=True)
        글상자(slide, 여백 + Inches(1.3), 위, Inches(9), Inches(0.9),
             [줄], Pt(32), 흰색, 굵게=True, 세로정렬=MSO_ANCHOR.MIDDLE)
    쪽번호(slide, 번호, 흰색)


def 본문(slide, 장, 번호):
    바탕(slide, 흰색)
    제목달기(slide, 장["제목"])
    위 = Inches(2.5)
    if 장["큰숫자"]:
        글상자(slide, 여백, 위, Inches(11), Inches(2.0),
             [장["큰숫자"]], Pt(110), 강조색, 굵게=True, 줄간격=1.0)
        위 = Inches(4.8)
    글상자(slide, 여백, 위, Inches(11.5), Inches(2.5),
         ["• " + 줄 for 줄 in 장["본문"][:3]], 본문크기, 기본색, 문단사이=Pt(18))
    쪽번호(slide, 번호)


def 단계(slide, 장, 번호):
    바탕(slide, 흰색)
    제목달기(slide, 장["제목"])
    줄들 = 장["본문"][:3]
    칸너비, 화살표 = Inches(3.3), Inches(0.75)
    간격 = (가로 - 여백 * 2 - 칸너비 * len(줄들)) / max(len(줄들) - 1, 1)
    for i, 줄 in enumerate(줄들):
        왼 = 여백 + int((칸너비 + 간격) * i)
        상자 = 도형(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 왼, Inches(3.0), 칸너비, Inches(2.4),
                  강조색 if i == len(줄들) - 1 else 기본색)
        tf = 상자.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = Inches(0.25)
        # "1~2주 도구 만들기" 처럼 앞말과 뒷말을 두 줄로 나눠 보기 좋게
        앞, _, 뒤 = 줄.partition("/" if "/" in 줄 else " ")
        for j, 조각 in enumerate([앞, 뒤] if 뒤 else [줄]):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = 조각
            글꼴지정(r, 본문크기, 흰색, 굵게=True)
        if i < len(줄들) - 1:
            도형(slide, MSO_SHAPE.RIGHT_ARROW, 왼 + 칸너비 + int((간격 - 화살표) / 2),
                 Inches(4.0), 화살표, Inches(0.4), 기본색)
    쪽번호(slide, 번호)


def 표(slide, 장, 번호):
    바탕(slide, 흰색)
    제목달기(slide, 장["제목"])
    행들 = 장["표"]
    tbl = slide.shapes.add_table(len(행들), len(행들[0]), 여백, Inches(2.5),
                                 Inches(9), Inches(0.75) * len(행들)).table
    for r, 행 in enumerate(행들):
        for c, 값 in enumerate(행):
            칸 = tbl.cell(r, c)
            칸.fill.solid()
            칸.fill.fore_color.rgb = 기본색 if r == 0 else 흰색
            p = 칸.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = 값
            글꼴지정(run, Pt(24), 흰색 if r == 0 else 기본색, 굵게=(r == 0))
    쪽번호(slide, 번호)


def 차트(slide, 장, 번호):
    바탕(slide, 흰색)
    제목달기(slide, 장["제목"])
    머리, *행들 = 장["표"]
    data = CategoryChartData()
    data.categories = [행[0] for 행 in 행들]
    for c, 이름 in enumerate(머리[1:], start=1):
        data.add_series(이름, [float(행[c]) for 행 in 행들])
    ch = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, 여백, Inches(2.2),
                                가로 - 여백 * 2, Inches(4.7), data).chart
    ch.font.size, ch.font.name = Pt(24), 글꼴
    ch.font.color.rgb = 기본색
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.TOP
    ch.legend.include_in_layout = False
    ch.value_axis.has_major_gridlines = False
    ch.value_axis.visible = False
    plot = ch.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    plot.data_labels.font.size = Pt(24)
    plot.data_labels.number_format = '0.#"시간"'
    plot.data_labels.number_format_is_linked = False
    for 시리즈, 색 in zip(plot.series, [기본색, 강조색]):
        시리즈.format.fill.solid()
        시리즈.format.fill.fore_color.rgb = 색
    쪽번호(slide, 번호)


# ── 실행 ──
def 만들기(원고, 저장):
    prs = Presentation()
    prs.slide_width, prs.slide_height = 가로, 세로
    빈틀 = prs.slide_layouts[6]
    장들 = 원고읽기(원고)
    for 번호, 장 in enumerate(장들, start=1):
        slide = prs.slides.add_slide(빈틀)
        종류 = 장["종류"]
        if 종류 == "표지":
            표지(slide, 장)
        elif 종류 == "마지막":
            마지막(slide, 장, 번호)
        elif 종류 == "단계":
            단계(slide, 장, 번호)
        elif 종류 == "표":
            표(slide, 장, 번호)
        elif 종류 == "차트":
            차트(slide, 장, 번호)
        else:
            본문(slide, 장, 번호)
        if 장["대본"]:
            slide.notes_slide.notes_text_frame.text = "\n".join(장["대본"])
        노트 = f" (노트 {len(' '.join(장['대본']))}자)" if 장["대본"] else ""
        print(f"{번호:>2}장 [{종류}] {장['제목']}{노트}")
    Path(저장).parent.mkdir(parents=True, exist_ok=True)
    prs.save(저장)
    print(f"저장: {저장} ({len(장들)}장)")


if __name__ == "__main__":
    여기 = Path(__file__).resolve().parent
    원고 = sys.argv[1] if len(sys.argv) > 1 else 여기 / "슬라이드원고.md"
    저장 = sys.argv[2] if len(sys.argv) > 2 else 여기.parent / "결과" / "업무자동화_제안.pptx"
    만들기(원고, 저장)

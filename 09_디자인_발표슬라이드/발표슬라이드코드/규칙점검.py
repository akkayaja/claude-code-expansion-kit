"""완성된 .pptx 를 열어 template/슬라이드_규칙.md 를 지켰는지 잰다.

사용법:  uv run python 발표슬라이드코드/규칙점검.py [발표.pptx]
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

제목최소, 본문최소 = Pt(36), Pt(24)
본문최대줄, 한줄글자 = 3, 22          # "20자 안팎" → 22자까지 허용
흰색 = "FFFFFF"


def 글자들(slide):
    """(글자, 크기, 굵게, 색) 목록. 쪽번호(아주 작은 숫자)는 뺀다."""
    결과 = []
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if not r.text.strip() or (r.text.isdigit() and r.font.size and r.font.size < Pt(20)):
                    continue
                색 = str(r.font.color.rgb) if r.font.color and r.font.color.type else None
                결과.append((r.text.strip(), r.font.size, r.font.bold, 색))
    return 결과


def 쓰인색(slide):
    색들 = set()
    for sh in slide.shapes:
        try:
            if sh.fill.type == 1:          # 단색 채우기
                색들.add(str(sh.fill.fore_color.rgb))
        except (AttributeError, TypeError):
            pass
        if sh.has_chart:
            for s in sh.chart.plots[0].series:
                색들.add(str(s.format.fill.fore_color.rgb))
    색들 |= {c for *_, c in 글자들(slide) if c}
    if slide.background.fill.type == 1:
        색들.add(str(slide.background.fill.fore_color.rgb))
    return 색들 - {흰색}


def 점검(경로):
    prs = Presentation(경로)
    장수 = len(prs.slides)
    문제들, 전체색 = [], set()
    print(f"| 장 | 제목 | 제목pt | 본문 줄 | 가장 긴 줄 | 본문 최소pt | 결과 |")
    print(f"|---|---|---|---|---|---|---|")
    for i, slide in enumerate(prs.slides, start=1):
        글 = 글자들(slide)
        굵은큰글 = [g for g in 글 if g[1] and g[1] >= 제목최소 and g[2]]
        제목 = 굵은큰글[0] if 굵은큰글 else None
        본문 = [g for g in 글 if g is not 제목 and not (g[1] and g[1] >= Pt(80))]  # 큰 숫자는 따로
        본문 = [g for g in 본문 if not g[0].isdigit()]                              # 동그라미 번호 뺌
        이번 = []
        if not 제목:
            이번.append("제목 36pt↑ 없음")
        본문줄 = [g[0].lstrip("• ") for g in 본문]
        # 단계 상자는 '앞말/뒷말' 2조각이 한 줄이므로 상자 수로 센다
        상자수 = sum(1 for sh in slide.shapes if sh.has_text_frame and sh.shape_type == 1 and sh.text_frame.text.strip()
                   and not sh.text_frame.text.strip().isdigit())
        줄수 = 상자수 if 상자수 >= 2 else len(본문줄)
        if slide.shapes and any(sh.has_chart or sh.has_table for sh in slide.shapes):
            줄수 = 0
        if 줄수 > 본문최대줄:
            이번.append(f"본문 {줄수}줄")
        긴줄 = max((len(t) for t in 본문줄), default=0)
        if 긴줄 > 한줄글자:
            이번.append(f"한 줄 {긴줄}자")
        작은 = min((g[1] for g in 본문 if g[1]), default=None)
        if 작은 and 작은 < 본문최소:
            이번.append(f"본문 {작은.pt:.0f}pt")
        전체색 |= 쓰인색(slide)
        표시 = "✅" if not 이번 else "⚠️ " + ", ".join(이번)
        제목칸 = f"{제목[0]} | {제목[1].pt:.0f}" if 제목 else "- | -"
        작은칸 = f"{작은.pt:.0f}" if 작은 else "-"
        print(f"| {i} | {제목칸} | {줄수} | {긴줄}자 | {작은칸} | {표시} |")
        문제들 += [f"{i}장: {m}" for m in 이번]

    차트수 = sum(1 for s in prs.slides for sh in s.shapes if sh.has_chart)
    표수 = sum(1 for s in prs.slides for sh in s.shapes if sh.has_table)
    첫장 = " ".join(g[0] for g in 글자들(prs.slides[0]))
    끝장 = " ".join(g[0] for g in 글자들(prs.slides[-1]))
    print()
    print(f"- 장 수: {장수}장 (목표 8~10) {'✅' if 8 <= 장수 <= 10 else '⚠️'}")
    print(f"- 차트 {차트수}개 / 표 {표수}개 {'✅' if 차트수 >= 1 else '⚠️'}")
    print(f"- 쓰인 색(흰 바탕 제외): {sorted(전체색)} → {len(전체색)}가지 {'✅' if len(전체색) <= 2 else '⚠️'}")
    print(f"- 첫 장 발표자 표시: {'✅' if '발표자' in 첫장 else '⚠️'}")
    print(f"- 마지막 장 요청 사항: {'✅' if '승인' in 끝장 or '요청' in 끝장 else '⚠️'}")
    print(f"- 규칙 위반: {len(문제들)}건" + ("".join("\n  - " + m for m in 문제들)))


if __name__ == "__main__":
    기본 = Path(__file__).resolve().parent.parent / "결과" / "업무자동화_제안.pptx"
    점검(sys.argv[1] if len(sys.argv) > 1 else 기본)

"""미션 5: 노션 '학습기록'에서 이번 주 기록만 읽어 와 요약하기.

'이번 주' 기준 (실행할 때 고르기)
    python3 노션코드/4_이번주요약.py          ← 이번 주 월요일 ~ 일요일 (달력 기준)
    python3 노션코드/4_이번주요약.py --7일    ← 오늘 포함 지난 7일
    python3 노션코드/4_이번주요약.py 2026-11-22   ← 그 날짜가 있는 주 (연습용)

- 걸러 내기는 노션에게 맡겨요 ('날짜' 칸이 시작일~끝일 사이인 것만 달라고 요청).
- 화면에 보여 주고, 결과/이번주요약_날짜.md 로도 저장해요.
"""
import os
import sys
from collections import Counter
from datetime import date, timedelta

import 노션도구 as nt

args = [a for a in sys.argv[1:] if not a.startswith("--")]
today = date.fromisoformat(args[0]) if args else date.today()
if "--7일" in sys.argv:
    start, end, label = today - timedelta(days=6), today, "지난 7일"
else:
    start = today - timedelta(days=today.weekday())         # 그 주 월요일
    end, label = start + timedelta(days=6), "이번 주(월~일)"

db_id = nt.database_id()
res = nt.call("POST", f"databases/{db_id}/query", {
    "filter": {"and": [
        {"property": "날짜", "date": {"on_or_after": start.isoformat()}},
        {"property": "날짜", "date": {"on_or_before": end.isoformat()}},
    ]},
    "sorts": [{"property": "날짜", "direction": "ascending"}],
    "page_size": 100,
})


def text(prop):
    """노션 칸 하나를 사람이 읽는 글자로."""
    t = prop["type"]
    if t in ("title", "rich_text"):
        return "".join(x["plain_text"] for x in prop[t])
    if t == "select":
        return prop["select"]["name"] if prop["select"] else ""
    if t == "date":
        return prop["date"]["start"] if prop["date"] else ""
    if t == "number":
        return prop["number"]
    return prop.get(t)


rows = [{k: text(v) for k, v in p["properties"].items()} for p in res["results"]]
kits = Counter(r["키트"] or "(없음)" for r in rows)
minutes = [r["걸린 시간(분)"] for r in rows if r["걸린 시간(분)"] is not None]
days = Counter(r["날짜"] for r in rows)

lines = [f"# 📅 {label} 학습 요약 ({start} ~ {end})", ""]
if not rows:
    lines.append("이 기간에 기록이 없어요.")
else:
    lines += [
        f"- 기록 **{len(rows)}개**, 공부한 날 **{len(days)}일**",
        "- 키트별: " + ", ".join(f"{k} {n}개" for k, n in kits.most_common()),
        f"- 걸린 시간: 적힌 {len(minutes)}개 합계 **{sum(minutes)}분**"
        + (f" (나머지 {len(rows) - len(minutes)}개는 시간 칸이 비어 있음)" if len(minutes) < len(rows) else ""),
        f"- 가장 많이 한 날: {days.most_common(1)[0][0]} ({days.most_common(1)[0][1]}개)",
        "", "## 기록", "",
    ]
    for r in rows:
        lines.append(f"- **{r['제목']}** ({r['날짜']}, {r['키트']}) — {r['얻은 능력']}")

report = "\n".join(lines)
print(report)
os.makedirs(nt.OUT_DIR, exist_ok=True)
tag = "7일" if "--7일" in sys.argv else "이번주"
out = os.path.join(nt.OUT_DIR, f"요약_{tag}_{today}.md")              # 기준마다 다른 파일
with open(out, "w", encoding="utf-8") as f:
    f.write(report + "\n")
print(f"\n💾 저장: 결과/{os.path.basename(out)}")

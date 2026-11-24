"""미션 4: 1단계 학습일지/ 의 md 파일들을 노션 '학습기록' 표에 한꺼번에 넣기 (중복 방지).

각 md 파일에서 꺼내는 것
  제목       ← 파일 이름 (01_엑셀자동화.md → '01 엑셀자동화')
  날짜       ← '실습 날짜:' 줄의 첫 날짜 (YYYY-MM-DD)
  키트       ← '1단계'
  얻은 능력  ← '얻은 능력:' 줄 (굵게·코드 표시는 빼고, 2000자까지)
  깃허브 링크 ← GitHub 1단계 저장소의 그 학습일지 주소
  걸린 시간·난이도 ← 학습일지에 적혀 있지 않아서 비워 둠 (지어내지 않기)

중복 방지: 노션 표에 이미 있는 '제목'은 건너뛰어요. 여러 번 실행해도 안전해요.

실행 (20 폴더에서):
    python3 노션코드/3_학습일지옮기기.py --미리보기   ← 노션에 안 넣고 무엇을 넣을지만 보기
    python3 노션코드/3_학습일지옮기기.py              ← 진짜 넣기
"""
import glob
import os
import re
import sys
import time
from urllib.parse import quote

import 노션도구 as nt

KIT1_LOG = os.path.normpath(os.path.join(nt.FOLDER, "..", "..", "클로드코드_실습키트", "학습일지"))
GITHUB = "https://github.com/akkayaja/claude-code-practice-kit/blob/main/"
PREVIEW = "--미리보기" in sys.argv


def clean(text):
    """마크다운 꾸밈(**굵게**, `코드`, [링크](주소))을 빼고 글자만 남긴다."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text.replace("**", "").replace("`", "").strip()


def read_log(path):
    name = os.path.basename(path)[:-3]                       # '01_엑셀자동화'
    with open(path, encoding="utf-8") as f:
        text = f.read()
    day = re.search(r"실습 날짜:\**\s*(\d{4}-\d{2}-\d{2})", text)
    skill = re.search(r"얻은 능력:\**\s*(.+)", text)
    return {
        "제목": name.replace("_", " ", 1),
        "날짜": day.group(1) if day else None,
        "얻은 능력": clean(skill.group(1))[:2000] if skill else "",
        "깃허브 링크": GITHUB + quote("학습일지/" + os.path.basename(path)),
    }


def existing_titles(db_id):
    """노션 표에 이미 있는 제목 전부 (100개씩 넘겨 가며 다 읽기)."""
    titles, cursor = set(), None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        res = nt.call("POST", f"databases/{db_id}/query", body)
        for page in res["results"]:
            t = page["properties"]["제목"]["title"]
            titles.add("".join(x["plain_text"] for x in t))
        if not res.get("has_more"):
            return titles
        cursor = res["next_cursor"]


logs = [read_log(p) for p in sorted(glob.glob(os.path.join(KIT1_LOG, "*.md")))]
db_id = nt.database_id()
have = existing_titles(db_id)
todo = [r for r in logs if r["제목"] not in have]

print(f"📚 1단계 학습일지 {len(logs)}개 / 노션에 이미 있음 {len(logs) - len(todo)}개 / 넣을 것 {len(todo)}개")
for r in todo:
    print(f"   {r['제목']:<16} {r['날짜'] or '날짜없음'}  {r['얻은 능력'][:30]}")
if PREVIEW:
    raise SystemExit("👀 미리보기라서 노션에는 넣지 않았어요.")

added = 0
for r in todo:
    props = {
        "제목": {"title": [{"text": {"content": r["제목"]}}]},
        "키트": {"select": {"name": "1단계"}},
        "얻은 능력": {"rich_text": [{"text": {"content": r["얻은 능력"]}}]},
        "깃허브 링크": {"url": r["깃허브 링크"]},
    }
    if r["날짜"]:
        props["날짜"] = {"date": {"start": r["날짜"]}}
    nt.call("POST", "pages", {"parent": {"database_id": db_id}, "properties": props})
    added += 1
    time.sleep(0.35)                                          # 노션은 1초에 3번 정도까지만 받아요
print(f"✅ 노션에 {added}개 넣었어요.")

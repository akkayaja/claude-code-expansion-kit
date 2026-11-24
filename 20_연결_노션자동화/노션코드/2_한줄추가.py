"""미션 3: 노션 '학습기록' 표에 기록 한 줄(카드 한 장) 추가하기.

실행 (20 폴더에서):
    python3 노션코드/2_한줄추가.py                       ← 연습용 기본 한 줄
    python3 노션코드/2_한줄추가.py "제목" "얻은 능력" 분 난이도
      예) python3 노션코드/2_한줄추가.py "20 연결 노션자동화" "코드로 노션에 기록 쌓기" 60 보통
- 날짜는 오늘, 키트는 '확장'으로 넣어요.
- 같은 제목이 이미 있으면 넣지 않아요 (중복 방지).
"""
import sys
from datetime import date

import 노션도구 as nt

args = sys.argv[1:] + [None] * 4
title = args[0] or "20 연결 노션자동화 (연습 한 줄)"
skill = args[1] or "스크립트로 노션 데이터베이스에 한 줄 추가하기"
minutes = int(args[2]) if args[2] else 10
level = args[3] or "쉬움"

db_id = nt.database_id()

# 1) 같은 제목이 있는지 먼저 물어보기 (중복 방지)
same = nt.call("POST", f"databases/{db_id}/query",
               {"filter": {"property": "제목", "title": {"equals": title}}})
if same["results"]:
    raise SystemExit(f"👌 '{title}' 은(는) 이미 있어요. 넣지 않았어요.")

# 2) 카드 한 장 만들기: 칸 이름마다 노션이 원하는 모양으로 값 넣기
page = nt.call("POST", "pages", {
    "parent": {"database_id": db_id},
    "properties": {
        "제목": {"title": [{"text": {"content": title}}]},
        "날짜": {"date": {"start": date.today().isoformat()}},
        "키트": {"select": {"name": "확장"}},
        "얻은 능력": {"rich_text": [{"text": {"content": skill}}]},
        "걸린 시간(분)": {"number": minutes},
        "난이도": {"select": {"name": level}},
    },
})
print(f"✅ 추가했어요: {title} / {date.today()} / {minutes}분 / {level}")
print(f"   노션에서 보기: {page['url']}")

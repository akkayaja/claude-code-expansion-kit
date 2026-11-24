"""미션 1 마무리: '학습기록' 표에 칸 7개를 학습기록_DB구조.md 대로 만들기.

- 처음부터 있는 제목 칸('이름')은 이름만 '제목'으로 바꿔요.
- 나머지 6칸은 없으면 새로 만들고, 이미 있으면 종류를 맞춰요. (여러 번 실행해도 안전)
- 끝나면 데이터베이스 ID를 보여 줘요 → 원하면 .env 의 NOTION_DATABASE_ID 에 넣어요.

실행 (20 폴더에서): python3 노션코드/1_칸만들기.py
"""
import 노션도구 as nt

COLUMNS = {
    "날짜": {"date": {}},
    "키트": {"select": {"options": [{"name": "1단계", "color": "blue"},
                                    {"name": "2단계", "color": "green"},
                                    {"name": "확장", "color": "purple"}]}},
    "얻은 능력": {"rich_text": {}},
    "걸린 시간(분)": {"number": {"format": "number"}},
    "난이도": {"select": {"options": [{"name": "쉬움", "color": "green"},
                                     {"name": "보통", "color": "yellow"},
                                     {"name": "어려움", "color": "red"}]}},
    "깃허브 링크": {"url": {}},
}

db_id = nt.database_id()
db = nt.call("GET", f"databases/{db_id}")
props = db["properties"]
title_name = next(n for n, p in props.items() if p["type"] == "title")

changes = {}
if title_name != "제목":
    changes[title_name] = {"name": "제목"}
for name, spec in COLUMNS.items():
    kind = next(iter(spec))
    if name not in props or props[name]["type"] != kind:
        changes[name] = spec

if changes:
    db = nt.call("PATCH", f"databases/{db_id}", {"properties": changes})
    print(f"✏️  바꾼 칸 {len(changes)}개: {', '.join(changes)}")
else:
    print("👌 이미 칸이 다 맞아요. 바꿀 것 없음")

KOR = {"title": "제목", "date": "날짜", "select": "선택", "rich_text": "텍스트",
       "number": "숫자", "url": "URL"}
print("\n지금 표의 칸:")
for name, p in db["properties"].items():
    print(f"   {name:<10} {KOR.get(p['type'], p['type'])}")
print(f"\n데이터베이스 ID: {db_id}")

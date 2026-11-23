"""CSV 한 개를 읽어서 영상 설정 파일(data.js)을 만든다.

사용법:
    python3 설정만들기.py CSV파일 --주제 카페 --아이콘 ☕

CSV는 3칸이어야 해요: 도시, 연도, 숫자 (첫 줄은 제목 줄)
"""
import argparse
import csv
import json

parser = argparse.ArgumentParser(description="CSV → data.js 영상 설정 만들기")
parser.add_argument("csv파일")
parser.add_argument("--주제", required=True, help="예: 카페, 편의점")
parser.add_argument("--아이콘", default="📊", help="제목에 붙일 그림문자")
parser.add_argument("--단위", default="곳", help="숫자 뒤에 붙일 말 (예: 곳, 개)")
parser.add_argument("--출처", default="가상 데이터 (연습용)")
parser.add_argument("--출력", default="data.js")
args = parser.parse_args()

# 1) CSV 읽기: {도시: {연도: 숫자}}
표 = {}
with open(args.csv파일, encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    next(reader)  # 제목 줄 건너뛰기
    for 도시, 연도, 숫자 in reader:
        표.setdefault(도시, {})[int(연도)] = int(숫자)

연도 = sorted({y for 값들 in 표.values() for y in 값들})
데이터 = {도시: [값들[y] for y in 연도] for 도시, 값들 in 표.items()}
첫해, 끝해 = 연도[0], 연도[-1]

# 2) 계산: 가장 많이 늘어난 도시(늘어난 개수 기준), 증가율, 해마다 1위
늘어난수 = {도시: v[-1] - v[0] for 도시, v in 데이터.items()}
주인공 = max(늘어난수, key=늘어난수.get)
처음값, 마지막값 = 데이터[주인공][0], 데이터[주인공][-1]
증가율 = round((마지막값 / 처음값 - 1) * 100)
처음1위 = max(데이터, key=lambda c: 데이터[c][0])
마지막1위 = max(데이터, key=lambda c: 데이터[c][-1])

# 3) 한글 조사: 받침 있으면 "이", 없으면 "가" (카페가 / 편의점이)
끝글자 = args.주제[-1]
받침있음 = "가" <= 끝글자 <= "힣" and (ord(끝글자) - 0xAC00) % 28 != 0

설정 = {
    "주제": args.주제,
    "조사": "이" if 받침있음 else "가",
    "아이콘": args.아이콘,
    "단위": args.단위,
    "출처": args.출처,
    "연도": 연도,
    "기간": 끝해 - 첫해 + 1,
    "데이터": 데이터,
    "주인공": 주인공,
    "처음값": 처음값,
    "마지막값": 마지막값,
    "증가율": 증가율,
    "처음1위": 처음1위,
    "마지막1위": 마지막1위,
}
with open(args.출력, "w", encoding="utf-8") as f:
    f.write("// 설정만들기.py 가 자동으로 만든 파일이에요. 직접 고치지 말고 CSV를 바꾼 뒤 다시 만드세요.\n")
    f.write("window.영상설정 = " + json.dumps(설정, ensure_ascii=False, indent=2) + ";\n")

print(f"✅ {args.출력} 만들기 완료")
print(f"   주제: {args.주제} / 기간: {첫해}~{끝해} ({len(연도)}년) / 도시 {len(데이터)}곳")
print(f"   가장 많이 늘어난 도시: {주인공} ({처음값:,} → {마지막값:,}, +{늘어난수[주인공]:,}, +{증가율}%)")
print(f"   1위: {첫해}년 {처음1위} → {끝해}년 {마지막1위}")

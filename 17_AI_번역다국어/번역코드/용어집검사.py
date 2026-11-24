"""번역문이 용어집을 지켰는지 검사한다.

사용법: python3 번역코드/용어집검사.py 번역문.md 언어
  언어: 영어 / 일본어 / 중국어(간체)  (용어집.csv 첫 줄의 이름)

기준: 원문(한국어)에 나온 용어집 단어마다,
      번역문에 정해진 번역어가 '글자 그대로' 같은 횟수 이상 들어 있으면 통과.
      (영어는 대소문자까지 같아야 통과)
"""
import csv
import sys
from pathlib import Path

폴더 = Path(__file__).resolve().parent.parent
원문 = (폴더 / "data/카페_안내문.md").read_text(encoding="utf-8")
용어집 = list(csv.DictReader(open(폴더 / "data/용어집.csv", encoding="utf-8-sig")))

번역파일, 언어 = sys.argv[1], sys.argv[2]
번역문 = Path(번역파일).read_text(encoding="utf-8")

print(f"검사: {번역파일} ({언어})\n")
print(f"| 한국어 | 정해진 번역어 | 원문 횟수 | 번역문 횟수 | 결과 |")
print(f"|---|---|---|---|---|")
통과 = 0
검사수 = 0
for 줄 in 용어집:
    한 = 줄["한국어"]
    번 = 줄[언어]
    원문횟수 = 원문.count(한)
    if 원문횟수 == 0:
        continue  # 원문에 없는 단어는 검사하지 않음
    검사수 += 1
    번역횟수 = 번역문.count(번)
    결과 = "✅ 통과" if 번역횟수 >= 원문횟수 else "❌ 안 지킴"
    if 번역횟수 >= 원문횟수:
        통과 += 1
    print(f"| {한} | {번} | {원문횟수} | {번역횟수} | {결과} |")

print(f"\n합계: {통과} / {검사수} 통과")

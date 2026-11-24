"""정답 / 맥 돋보기(Vision) / Claude 직접 읽기 세 가지를 비교해요.
그리고 Claude가 읽은 품목 금액을 더해서 합계와 맞는지 검산해요.
사용법: python3 OCR코드/세방법비교.py   (16번 폴더에서 실행)
"""
import csv


def 읽기(경로):
    with open(경로, encoding="utf-8-sig") as f:
        return {행["파일"]: 행 for 행 in csv.DictReader(f)}


정답 = 읽기("정답_영수증.csv")
비전 = 읽기("결과/영수증_결과.csv")
클로드 = 읽기("결과/Claude_직접읽기.csv")

점수 = {"Vision": 0, "Claude": 0}
print("[1] 가게·날짜·합계 3칸이 정답과 모두 같은가")
for 파일, 답 in 정답.items():
    결과줄 = [파일]
    for 이름, 표 in [("Vision", 비전), ("Claude", 클로드)]:
        맞음 = all(표[파일][칸] == 답[칸] for 칸 in ["가게", "날짜", "합계"])
        점수[이름] += 맞음
        결과줄.append(f"{이름} {'O' if 맞음 else 'X'}")
    print("  " + "  ".join(결과줄))
print(f"  → Vision {점수['Vision']}/6, Claude {점수['Claude']}/6\n")

print("[2] Claude가 읽은 품목 금액을 더하면 합계와 같은가 (검산)")
for 파일, 행 in 클로드.items():
    금액들 = [int(품목.split()[-1]) for 품목 in 행["품목"].split(" / ")]
    더한값 = sum(금액들)
    표시 = "O" if 더한값 == int(행["합계"]) else "X"
    print(f"  {파일} {' + '.join(map(str, 금액들))} = {더한값} / 합계 {행['합계']} {표시}")

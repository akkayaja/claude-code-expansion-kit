"""영수증 사진 6장을 글자 인식한 뒤, 가게·날짜·합계만 골라 CSV로 저장해요.
사용법: python3 OCR코드/영수증표만들기.py   (16번 폴더에서 실행)
먼저 swiftc OCR코드/글자읽기.swift -o 결과/ocr 로 '결과/ocr' 프로그램을 (이름은 꼭 영어로) 만들어 두어야 해요.
"""
import csv
import re
import subprocess
from pathlib import Path

사진들 = sorted(Path("images").glob("영수증_*.png"))
행들 = []

for 사진 in 사진들:
    # 1) 맥 돋보기로 글자 읽기 (줄 목록)
    글 = subprocess.run(["결과/ocr", str(사진)], capture_output=True, text=True).stdout
    줄들 = [줄.strip() for 줄 in 글.splitlines() if 줄.strip()]
    Path(f"결과/{사진.stem}.txt").write_text(글, encoding="utf-8")  # 원본 글자도 보관

    # 2) 가게 = 맨 첫 줄 (영수증 제목)
    가게 = 줄들[0] if 줄들 else ""

    # 3) 날짜 = "2026-11-13" 모양을 찾기 (숫자4-숫자2-숫자2)
    날짜 = ""
    for 줄 in 줄들:
        찾음 = re.search(r"\d{4}-\d{1,2}-\d{1,2}", 줄)
        if 찾음:
            날짜 = 찾음.group()
            break

    # 4) 합계 = "원"이 붙은 숫자 줄 → 쉼표·원 떼고 숫자만
    합계 = ""
    for 줄 in 줄들:
        if 줄.endswith("원") and re.search(r"\d", 줄):
            합계 = re.sub(r"[^\d]", "", 줄)
            break

    행들.append({"파일": 사진.name, "가게": 가게, "날짜": 날짜, "합계": 합계})
    print(사진.name, 가게, 날짜, 합계)

with open("결과/영수증_결과.csv", "w", newline="", encoding="utf-8-sig") as f:
    쓰기 = csv.DictWriter(f, fieldnames=["파일", "가게", "날짜", "합계"])
    쓰기.writeheader()
    쓰기.writerows(행들)

print(f"\n저장 완료: 결과/영수증_결과.csv ({len(행들)}장)")

"""지출 정리 도구: 1단계 05번(PDF 거래명세서) + 16번(영수증 사진)을 한 엑셀로 합쳐요.
사용법 (16번 폴더에서, 05번의 파이썬을 빌려 실행):
  ../../클로드코드_실습키트/05_PDF정보추출/.venv/bin/python OCR코드/지출정리.py
"""
import csv
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

PDF_엑셀 = Path("../../클로드코드_실습키트/05_PDF정보추출/결과/거래명세서_목록.xlsx")
영수증_CSV = Path("결과/영수증_결과.csv")
저장위치 = Path("결과/지출정리.xlsx")

지출 = []  # (날짜, 종류, 거래처, 금액, 원본파일)

# 1) PDF 거래명세서 (05번 결과 엑셀의 첫 시트)
시트 = load_workbook(PDF_엑셀)["거래명세서_목록"]
for 파일명, _번호, 날짜, 공급자, _공급가, _부가세, 합계 in 시트.iter_rows(min_row=2, values_only=True):
    지출.append((날짜, "PDF 거래명세서", 공급자, int(합계), 파일명))

# 2) 영수증 사진 (16번 결과 CSV)
with open(영수증_CSV, encoding="utf-8-sig") as f:
    for 행 in csv.DictReader(f):
        지출.append((행["날짜"], "영수증 사진", 행["가게"], int(행["합계"]), 행["파일"]))

지출.sort()  # 날짜 순서로

# 3) 엑셀로 저장: 시트1 지출목록, 시트2 종류별·월별 합계
wb = Workbook()
굵게 = Font(bold=True)
머리색 = PatternFill("solid", fgColor="DDEBF7")


def 머리글(ws, 칸들):
    ws.append(칸들)
    for 칸 in ws[1]:
        칸.font, 칸.fill = 굵게, 머리색


ws = wb.active
ws.title = "지출목록"
머리글(ws, ["날짜", "종류", "거래처", "금액", "원본파일"])
for 줄 in 지출:
    ws.append(list(줄))
ws.append(["", "", "총합계", sum(줄[3] for 줄 in 지출), ""])
ws.cell(ws.max_row, 3).font = ws.cell(ws.max_row, 4).font = 굵게

묶음 = defaultdict(lambda: [0, 0])  # (월, 종류) → [건수, 금액]
for 날짜, 종류, _, 금액, _ in 지출:
    묶음[(날짜[:7], 종류)][0] += 1
    묶음[(날짜[:7], 종류)][1] += 금액
ws2 = wb.create_sheet("월별_종류별_합계")
머리글(ws2, ["월", "종류", "건수", "금액"])
for (월, 종류), (건수, 금액) in sorted(묶음.items()):
    ws2.append([월, 종류, 건수, 금액])

for 시트 in (ws, ws2):
    for 칸 in 시트[1]:
        시트.column_dimensions[칸.column_letter].width = 18
    for 줄 in 시트.iter_rows(min_row=2):
        for 칸 in 줄:
            if isinstance(칸.value, int):
                칸.number_format = "#,##0"

wb.save(저장위치)

print(f"합친 지출 {len(지출)}건 (PDF {sum(1 for 줄 in 지출 if 줄[1].startswith('PDF'))}건 + 영수증 {sum(1 for 줄 in 지출 if 줄[1].startswith('영수증'))}건)")
for (월, 종류), (건수, 금액) in sorted(묶음.items()):
    print(f"  {월} {종류}: {건수}건 {금액:,}원")
print(f"총합계 {sum(줄[3] for 줄 in 지출):,}원 → {저장위치}")

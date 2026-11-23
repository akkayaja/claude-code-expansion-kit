# 도전 미션 2: 채널 통계 CSV → HTML 대시보드 파일 하나 만들기
# 실행: .venv/bin/python 결과/대시보드만들기.py   (06 폴더에서)
# CSV만 바꾸고 다시 실행하면 대시보드가 새 데이터로 다시 만들어져요.
import json
from pathlib import Path

import pandas as pd

CSV = Path("data/채널_영상통계.csv")
OUT = Path("결과/대시보드.html")

# 제목 유형 규칙 (제목분류.py와 같은 규칙)
유형규칙 = [
    ("단계 따라하기 실습", "숫자+실습형"),
    ("처음부터 따라하기 실습", "실습형"),
    ("가지만 알면 끝", "숫자형"),
    ("어떻게 하세요?", "질문형"),
    ("의 모든 것", "총정리형"),
    ("이렇게 하세요", "방법제시형"),
    ("솔직 후기", "후기형"),
]


def 유형찾기(제목):
    for 글자, 유형 in 유형규칙:
        if 글자 in 제목:
            return 유형
    return "기타"


df = pd.read_csv(CSV, encoding="utf-8-sig")
영상들 = [
    {
        "제목": r["제목"], "형식": r["형식"], "요일": r["요일"],
        "분": round(r["길이(초)"] / 60, 1), "조회수": int(r["조회수"]),
        "클릭률": float(r["클릭률(%)"]), "지속률": float(r["시청지속률(%)"]),
        "유형": 유형찾기(r["제목"]),
    }
    for _, r in df.iterrows()
]

틀 = Path(__file__).with_name("대시보드_틀.html").read_text(encoding="utf-8")
html = 틀.replace("__DATA__", json.dumps(영상들, ensure_ascii=False))
OUT.write_text(html, encoding="utf-8")
print(f"저장: {OUT}  (영상 {len(영상들)}개)")

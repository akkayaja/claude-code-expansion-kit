# 도전 미션 1: 제목 120개를 유형별로 나누고 클릭률·조회수 비교
# 실행: .venv/bin/python 결과/제목분류.py   (06 폴더에서)
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

CSV = Path("data/채널_영상통계.csv")
OUT = Path("결과")
plt.rcParams["font.family"] = "Apple SD Gothic Neo"
plt.rcParams["axes.unicode_minus"] = False

# 제목 틀(규칙) → 유형 이름. Claude가 120개 제목을 읽고 정한 7가지 유형이에요.
유형규칙 = [
    ("단계 따라하기 실습", "숫자+실습형"),   # 예: 업무 자동화 5단계 따라하기 실습
    ("처음부터 따라하기 실습", "실습형"),     # 예: GitHub 입문 처음부터 따라하기 실습
    ("가지만 알면 끝", "숫자형"),            # 예: 엑셀 자동화, 5가지만 알면 끝
    ("어떻게 하세요?", "질문형"),            # 예: 요즘 PDF 정리 어떻게 하세요?
    ("의 모든 것", "총정리형"),              # 예: 데이터 정리의 모든 것
    ("이렇게 하세요", "방법제시형"),          # 예: 회의록 AI, 이렇게 하세요
    ("솔직 후기", "후기형"),                 # 예: AI 공부 루틴 솔직 후기
]


def 유형찾기(제목):
    for 글자, 유형 in 유형규칙:
        if 글자 in 제목:
            return 유형
    return "기타"


df = pd.read_csv(CSV, encoding="utf-8-sig")
df["제목유형"] = df["제목"].apply(유형찾기)
df[["번호", "제목", "형식", "제목유형", "조회수", "클릭률(%)"]].to_csv(
    OUT / "제목분류표.csv", index=False, encoding="utf-8-sig")

# 유형별 평균 (클릭률은 전체, 조회수는 쇼츠/롱폼 따로)
표 = df.groupby("제목유형").agg(영상수=("번호", "count"), 평균클릭률=("클릭률(%)", "mean"))
조회 = df.pivot_table(index="제목유형", columns="형식", values="조회수", aggfunc="mean")
표 = 표.join(조회.add_prefix("평균조회_")).sort_values("평균클릭률", ascending=False)
print(표.round(2).to_string())
표.round(2).to_csv(OUT / "제목유형별_성과.csv", encoding="utf-8-sig")

# 그래프: 유형별 평균 클릭률 (숫자가 들어간 유형만 파란색)
fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=150)
색 = ["#2a78d6" if "숫자" in k else "#c9c8c2" for k in 표.index]
막대 = ax.barh(표.index[::-1], 표["평균클릭률"][::-1], color=색[::-1], height=0.55)
for b, v in zip(막대, 표["평균클릭률"][::-1]):
    ax.text(v + 0.05, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center",
            fontsize=10, color="#52514e")
ax.axvline(df["클릭률(%)"].mean(), color="#52514e", linewidth=1, linestyle="--")
ax.text(df["클릭률(%)"].mean() + 0.05, -0.75, "전체 평균", fontsize=9, color="#52514e")
ax.set_title("⑤ 숫자가 들어간 제목 유형만 클릭률이 높아요", fontsize=15, loc="left", pad=14)
ax.set_xlabel("평균 클릭률(%)", color="#52514e")
for 쪽 in ["top", "right", "bottom"]:
    ax.spines[쪽].set_visible(False)
ax.tick_params(colors="#52514e", length=0)
ax.xaxis.grid(True, color="#ecebe7")
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT / "그래프" / "5_제목유형별_클릭률.png")
print("저장: 결과/그래프/5_제목유형별_클릭률.png")

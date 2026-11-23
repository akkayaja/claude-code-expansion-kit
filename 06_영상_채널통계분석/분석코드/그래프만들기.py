# 채널 영상 통계 CSV로 그래프 4장을 만드는 스크립트
# 실행: .venv/bin/python 결과/그래프만들기.py   (06 폴더에서)
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 파일로만 저장
import matplotlib.pyplot as plt
import pandas as pd

# ── 설정 ─────────────────────────────────────────────
CSV = Path("data/채널_영상통계.csv")
OUT = Path("결과/그래프")
OUT.mkdir(parents=True, exist_ok=True)

강조색 = "#2a78d6"   # 눈여겨볼 막대
기본색 = "#c9c8c2"   # 나머지 막대
글자색 = "#52514e"
plt.rcParams["font.family"] = "Apple SD Gothic Neo"  # 맥 기본 한글 글꼴
plt.rcParams["axes.unicode_minus"] = False

# ── 데이터 읽기 ───────────────────────────────────────
df = pd.read_csv(CSV, encoding="utf-8-sig")
df["숫자제목"] = df["제목"].apply(lambda t: "숫자 있음" if re.search(r"\d", t) else "숫자 없음")
df["분"] = df["길이(초)"] / 60


def 꾸미기(ax, 제목, y이름):
    """축과 테두리를 연하게 정리"""
    ax.set_title(제목, fontsize=15, loc="left", pad=14, color="#0b0b0b")
    ax.set_ylabel(y이름, color=글자색)
    for 쪽 in ["top", "right", "left"]:
        ax.spines[쪽].set_visible(False)
    ax.spines["bottom"].set_color("#d8d7d2")
    ax.tick_params(colors=글자색, length=0)
    ax.yaxis.grid(True, color="#ecebe7")
    ax.set_axisbelow(True)


def 막대그래프(값, 강조, 제목, y이름, 파일, 단위=""):
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    색 = [강조색 if k in 강조 else 기본색 for k in 값.index]
    막대 = ax.bar(값.index, 값.values, color=색, width=0.55)
    for b, v in zip(막대, 값.values):
        글 = f"{v:,.0f}{단위}" if 단위 == "" else f"{v:.1f}{단위}"
        ax.text(b.get_x() + b.get_width() / 2, v, 글, ha="center", va="bottom",
                fontsize=10, color=글자색)
    꾸미기(ax, 제목, y이름)
    fig.tight_layout()
    fig.savefig(OUT / 파일)
    plt.close(fig)
    print("저장:", OUT / 파일)


# 1) 형식별 평균 조회수
형식 = df.groupby("형식")["조회수"].mean().reindex(["쇼츠", "롱폼"])
막대그래프(형식, ["쇼츠"], "① 쇼츠가 롱폼보다 평균 조회수가 1.3배 높아요",
          "평균 조회수(회)", "1_형식별_조회수.png")

# 2) 요일별 평균 조회수
요일순서 = ["월", "화", "수", "목", "금", "토", "일"]
요일 = df.groupby("요일")["조회수"].mean().reindex(요일순서)
막대그래프(요일, ["화", "목"], "② 화·목요일에 올린 영상의 조회수가 가장 높아요",
          "평균 조회수(회)", "2_요일별_조회수.png")

# 3) 제목에 숫자가 있을 때 클릭률
숫자 = df.groupby("숫자제목")["클릭률(%)"].mean().reindex(["숫자 있음", "숫자 없음"])
막대그래프(숫자, ["숫자 있음"], "③ 제목에 숫자가 있으면 클릭률이 1.6%p 높아요",
          "평균 클릭률(%)", "3_제목숫자_클릭률.png", 단위="%")

# 4) 롱폼 길이와 시청지속률 (점 하나 = 영상 하나)
롱폼 = df[df["형식"] == "롱폼"]
fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
긺 = 롱폼["분"] >= 12
ax.scatter(롱폼.loc[~긺, "분"], 롱폼.loc[~긺, "시청지속률(%)"], s=42, color=기본색,
           edgecolor="white", linewidth=1.5, label="12분 미만")
ax.scatter(롱폼.loc[긺, "분"], 롱폼.loc[긺, "시청지속률(%)"], s=42, color=강조색,
           edgecolor="white", linewidth=1.5, label="12분 이상")
ax.axvline(12, color=글자색, linewidth=1, linestyle="--")
ax.text(12.3, ax.get_ylim()[1] * 0.97, "12분", color=글자색, fontsize=10, va="top")
ax.set_xlabel("영상 길이(분)", color=글자색)
꾸미기(ax, "④ 롱폼이 12분을 넘으면 시청지속률이 뚝 떨어져요", "시청지속률(%)")
ax.legend(frameon=False, labelcolor=글자색)
fig.tight_layout()
fig.savefig(OUT / "4_롱폼길이_지속률.png")
plt.close(fig)
print("저장:", OUT / "4_롱폼길이_지속률.png")

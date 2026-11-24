"""4개 언어 안내문(md)을 읽어 언어 선택 버튼이 있는 웹페이지 한 장을 만든다.

사용법: python3 번역코드/페이지만들기.py
  읽는 것: data/카페_안내문.md (한국어), 결과/안내문_영어·일본어·중국어.md
  만드는 것: 결과/다국어카페.html
디자인은 1단계 11번 '오늘의 온기' 페이지(색·카드·다크모드)를 본떴다.
번역문 파일을 그대로 읽어 넣으므로, 용어집 검사를 통과한 글이 페이지에도 그대로 들어간다.
"""
import csv
import json
import re
from pathlib import Path

폴더 = Path(__file__).resolve().parent.parent
파일들 = {
    "ko": 폴더 / "data/카페_안내문.md",
    "en": 폴더 / "결과/안내문_영어.md",
    "ja": 폴더 / "결과/안내문_일본어.md",
    "zh": 폴더 / "결과/안내문_중국어.md",
}
용어집열 = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(간체)"}
용어집 = list(csv.DictReader(open(폴더 / "data/용어집.csv", encoding="utf-8-sig")))
가게이름 = next(줄 for 줄 in 용어집 if 줄["한국어"] == "봄날카페")

# 안내문에 없는 화면 글자(버튼·한 줄 소개·바닥글)만 따로 정한다
화면글자 = {
    "ko": {"tagline": "봄날처럼 포근한 동네 카페", "btn": "메뉴 보기", "footer": "실습용 가상 카페입니다."},
    "en": {"tagline": "A cozy neighborhood cafe, warm as a spring day", "btn": "See Menu", "footer": "This is a fictional cafe for practice."},
    "ja": {"tagline": "春の日のようにあたたかい街のカフェ", "btn": "メニューを見る", "footer": "練習用の架空のカフェです。"},
    "zh": {"tagline": "如春日般温暖的社区咖啡馆", "btn": "查看菜单", "footer": "这是用于练习的虚构咖啡馆。"},
}

def 읽기(경로):
    제목, 소제목, 메뉴, 규칙 = "", [], [], []
    for 줄 in 경로.read_text(encoding="utf-8").splitlines():
        if 줄.startswith("# "):
            제목 = 줄[2:].strip()
        elif 줄.startswith("## "):
            소제목.append(줄[3:].strip())
        elif 줄.startswith("- "):
            m = re.match(r"- \*\*(.+?)\*\*\s*[:：]\s*(.+)", 줄)
            if m:
                메뉴.append({"name": m.group(1), "desc": m.group(2)})
            else:
                규칙.append(줄[2:].strip())
    return {"title": 제목, "menuTitle": 소제목[0], "rulesTitle": 소제목[1], "menu": 메뉴, "rules": 규칙}

글 = {}
for 언어, 경로 in 파일들.items():
    글[언어] = {**읽기(경로), "cafe": 가게이름[용어집열[언어]], **화면글자[언어]}
    print(f"{언어}: 메뉴 {len(글[언어]['menu'])}개, 규칙 {len(글[언어]['rules'])}개")

틀 = (폴더 / "번역코드/페이지틀.html").read_text(encoding="utf-8")
결과 = 틀.replace("/*__TEXTS__*/", json.dumps(글, ensure_ascii=False, indent=1))
(폴더 / "결과/다국어카페.html").write_text(결과, encoding="utf-8")
print("저장: 결과/다국어카페.html")

"""도전 미션: 검수 → 재번역 되돌이 고리 (1단계 17번 '검수루프' 응용)

사용법 (03번 .venv의 파이썬으로 실행):
  ../../클로드코드_실습키트/03_메일분류/.venv/bin/python 번역코드/검수재번역.py 번역문.md 언어
  언어: 영어 / 일본어 / 중국어(간체)

흐름
  ① 검수: 원문 줄마다 용어집 단어가 있으면, 같은 줄 번역문에 정해진 번역어가 그대로 있는지 코드가 본다
  ② 재번역: 안 지킨 줄만 Claude에게 다시 번역시킨다 (지켜야 할 번역어를 같이 알려 줌)
  ③ 다시 검수 → 통과할 때까지, 최대 2번만 (무한 반복 방지)
결과: 결과/<원래이름>_재번역.md (고친 번역문), 결과/<원래이름>_재번역기록.md (회차별 기록)
"""
import csv
import sys
import time
from pathlib import Path

폴더 = Path(__file__).resolve().parent.parent          # 17_AI_번역다국어
금고 = 폴더.parent.parent / "클로드코드_실습키트" / "03_메일분류" / ".env"   # 1단계 03번 API 키 금고
모델 = "claude-sonnet-5-5"
최대재번역 = 2

원문줄 = (폴더 / "data/카페_안내문.md").read_text(encoding="utf-8").splitlines()
용어집 = list(csv.DictReader(open(폴더 / "data/용어집.csv", encoding="utf-8-sig")))


def 검수(번역줄, 언어):
    """안 지킨 줄 목록: [(줄번호, [(한국어, 번역어), ...]), ...]
    기준: 원문 그 줄에 용어집 한국어가 있는데, 번역문 같은 줄에 정해진 번역어가 글자 그대로 없으면 불통과."""
    문제 = []
    for i, (원, 번) in enumerate(zip(원문줄, 번역줄)):
        빠진것 = [(줄["한국어"], 줄[언어]) for 줄 in 용어집 if 줄["한국어"] in 원 and 줄[언어] not in 번]
        if 빠진것:
            문제.append((i, 빠진것))
    return 문제


def 다시번역(원문, 지금번역, 언어, 지킬말):
    """Claude에게 한 줄만 다시 번역시킨다."""
    import anthropic
    from dotenv import load_dotenv
    load_dotenv(금고)
    용어 = "\n".join(f"- {한} → {번}" for 한, 번 in 지킬말)
    지시문 = f"""너는 카페 안내문 번역가야. 한국어 한 줄을 {언어}로 번역해.
규칙
- [반드시 쓸 번역어]는 글자 하나 바꾸지 말고 그대로 넣어. (대소문자·띄어쓰기까지 그대로)
- 마크다운 기호(#, -, **)는 원문과 같은 자리에 그대로 둬.
- 번역한 한 줄만 출력하고 설명은 쓰지 마."""
    메시지 = f"[한국어 원문]\n{원문}\n\n[지금 번역 (용어집을 안 지킴)]\n{지금번역}\n\n[반드시 쓸 번역어]\n{용어}"
    응답 = anthropic.Anthropic().messages.create(
        model=모델, max_tokens=500, system=지시문,
        messages=[{"role": "user", "content": 메시지}],
    )
    글 = "".join(조각.text for 조각 in 응답.content if 조각.type == "text").strip()
    return 글.splitlines()[0] if 글 else 지금번역, 응답.usage


def main():
    번역파일, 언어 = Path(sys.argv[1]), sys.argv[2]
    번역줄 = 번역파일.read_text(encoding="utf-8").splitlines()
    if len(번역줄) != len(원문줄):
        sys.exit(f"줄 수가 달라요: 원문 {len(원문줄)}줄, 번역문 {len(번역줄)}줄 → 줄끼리 짝을 지을 수 없어요")

    기록 = [f"# 검수 → 재번역 기록: {번역파일.name} ({언어})", ""]
    토큰 = [0, 0]
    시작 = time.time()
    for 회차 in range(1, 최대재번역 + 2):                 # 검수는 최대 3번 (처음 + 재번역 후 2번)
        문제 = 검수(번역줄, 언어)
        print(f"① {회차}차 검수: {'✅ 통과' if not 문제 else f'❌ {len(문제)}줄 안 지킴'}")
        기록.append(f"## {회차}차 검수: {'통과' if not 문제 else f'{len(문제)}줄 안 지킴'}")
        if not 문제:
            break
        if 회차 > 최대재번역:
            print(f"⛔ 재번역 {최대재번역}번을 다 썼어요 → 사람이 직접 확인해 주세요")
            기록.append("재번역 횟수를 다 써서 멈춤 → 사람 확인 필요")
            break
        for i, 빠진것 in 문제:
            빠진말 = ", ".join(번 for _, 번 in 빠진것)
            print(f"   ② {i + 1}번째 줄 재번역 중... (빠진 말: {빠진말})")
            지킬말 = [(줄["한국어"], 줄[언어]) for 줄 in 용어집 if 줄["한국어"] in 원문줄[i]]
            새줄, 사용량 = 다시번역(원문줄[i], 번역줄[i], 언어, 지킬말)
            토큰[0] += 사용량.input_tokens
            토큰[1] += 사용량.output_tokens
            기록 += [f"- {i + 1}번째 줄 (빠진 말: {빠진말})", f"  - 전: `{번역줄[i]}`", f"  - 후: `{새줄}`"]
            번역줄[i] = 새줄
        기록.append("")

    저장 = 폴더 / "결과" / f"{번역파일.stem}_재번역.md"
    저장.write_text("\n".join(번역줄) + "\n", encoding="utf-8")
    요약 = f"걸린 시간 {time.time() - 시작:.1f}초, 토큰 입력 {토큰[0]} · 출력 {토큰[1]}"
    기록 += ["", 요약]
    (폴더 / "결과" / f"{번역파일.stem}_재번역기록.md").write_text("\n".join(기록) + "\n", encoding="utf-8")
    print(f"\n{요약}")
    print(f"저장: 결과/{저장.name}, 결과/{번역파일.stem}_재번역기록.md")


if __name__ == "__main__":
    main()

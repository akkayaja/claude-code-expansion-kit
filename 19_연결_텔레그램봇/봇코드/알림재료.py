"""봇이 보낼 내용 만들기: 1단계 14번 할 일 + 1단계 '내 프로젝트' 옷차림.

1단계 원본 파일은 고치지 않고 그대로 불러 써요.
- 할일:   14_자동실행봇/1_분류.py 를 실행해서 화면에 나온 글을 그대로 가져옴
- 옷차림: 내프로젝트_옷차림알림/2_옷차림.py 의 make_report() 를 불러 씀
          (기상청 키는 13_API연결/.env 에 있는 DATA_GO_KR_KEY 를 빌려 씀)

혼자 실행하면 (19 폴더에서): python3 봇코드/알림재료.py   ← 텔레그램 없이 내용만 미리 보기
"""
import importlib.util
import os
import subprocess
import sys

KIT1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "클로드코드_실습키트")
KIT1 = os.path.normpath(KIT1)
TODO_SCRIPT = os.path.join(KIT1, "14_자동실행봇", "1_분류.py")
OUTFIT_SCRIPT = os.path.join(KIT1, "내프로젝트_옷차림알림", "2_옷차림.py")
WEATHER_KEY_FOLDER = os.path.join(KIT1, "13_API연결")


def todo_text(day=None):
    """오늘(또는 day) 기준 할 일 분류 결과. '그 뒤' 묶음은 길어서 개수만 남긴다."""
    args = [sys.executable, TODO_SCRIPT] + ([day] if day else [])
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        return "❌ 할 일 목록을 읽지 못했어요.\n" + r.stderr.strip()[-300:]
    lines, skip = [], False
    for line in r.stdout.strip().splitlines():
        if line.startswith("⚪"):                  # '그 뒤' 묶음: 제목 줄만 남기고 목록은 생략
            lines.append(line + " (목록 생략)")
            skip = True
        elif not line.startswith("   "):
            skip = False
            lines.append(line)
        elif not skip:
            lines.append(line)
    return "📋 할 일 브리핑\n" + "\n".join(lines)


def outfit_text():
    """내일 광주 기온 + 옷차림 (1단계 옷차림 알림과 같은 내용)."""
    spec = importlib.util.spec_from_file_location("outfit", OUTFIT_SCRIPT)
    outfit = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        os.chdir(os.path.dirname(OUTFIT_SCRIPT))
        spec.loader.exec_module(outfit)
        outfit.forecast.HERE = WEATHER_KEY_FOLDER          # 기상청 키를 13번 .env 에서 찾게 함
        subject, body = outfit.make_report()
        return subject + "\n\n" + body
    except SystemExit as e:                                 # 키 없음·기상청 오류 등
        return f"❌ 날씨를 받지 못했어요: {e}"
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    print(todo_text())
    print("\n" + "=" * 40 + "\n")
    print(outfit_text())

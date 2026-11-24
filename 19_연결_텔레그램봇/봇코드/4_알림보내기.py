"""미션 4: 할 일 브리핑과 옷차림 알림을 텔레그램으로 받기 (메일 대신/메일과 함께).

- 1단계 14번·옷차림 알림은 그대로 두고, 같은 내용을 텔레그램으로 '먼저' 보내요.
- 자동 실행(launchd)에 이 파일 하나만 걸면 매일 받을 수 있어요.

실행 (19 폴더에서):
    python3 봇코드/4_알림보내기.py          ← 할 일 + 옷차림 둘 다
    python3 봇코드/4_알림보내기.py 할일     ← 할 일만
    python3 봇코드/4_알림보내기.py 날씨     ← 옷차림만
"""
import sys

import 텔레그램도구 as tg
import 알림재료

if not tg.MY_CHAT_ID:
    raise SystemExit("⚠️  .env 에 MY_CHAT_ID 가 없어요. 1_채팅ID찾기.py 로 먼저 알아내요.")

what = sys.argv[1] if len(sys.argv) > 1 else "둘다"
if what in ("할일", "둘다"):
    tg.send(tg.MY_CHAT_ID, 알림재료.todo_text())
    tg.log("미션4: 할 일 브리핑 보냄")
if what in ("날씨", "둘다"):
    tg.send(tg.MY_CHAT_ID, 알림재료.outfit_text())
    tg.log("미션4: 옷차림 알림 보냄")

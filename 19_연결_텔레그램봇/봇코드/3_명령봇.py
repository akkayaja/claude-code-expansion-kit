"""미션 3·5: 명령을 보내면 답하는 봇 (켜 두는 동안만 대답해요).

명령 (텔레그램 명령은 원래 영어만 되지만, 글자를 직접 비교해서 한글도 받아요)
  /start            인사 + 명령 목록
  /할일  /todo      1단계 14번 할 일 브리핑
  /날씨  /weather   내일 광주 기온 + 옷차림

미션 5 보안: .env 의 MY_CHAT_ID 가 아닌 사람이 말을 걸면 대답하지 않고 기록만 남겨요.
  python3 봇코드/3_명령봇.py              ← 나에게만 대답 (기본)
  python3 봇코드/3_명령봇.py --열어두기   ← 미션 3 연습용: 누구에게나 대답 (위험! 확인 후 바로 끄기)

끄기: 터미널에서 Ctrl + C
기록: 결과/봇기록.log
"""
import sys

import 텔레그램도구 as tg
import 알림재료

OPEN_TO_ALL = "--열어두기" in sys.argv

HELP = ("안녕하세요! 맥에 사는 비서 봇이에요 🤖\n"
        "/할일 (/todo) – 오늘 할 일 브리핑\n"
        "/날씨 (/weather) – 내일 광주 기온과 옷차림")


def answer(text):
    """받은 글에 맞는 대답을 만든다. 모르는 말이면 도움말."""
    cmd = text.strip().split()[0].split("@")[0].lower() if text.strip() else ""
    if cmd in ("/할일", "/todo", "할일"):
        return 알림재료.todo_text()
    if cmd in ("/날씨", "/weather", "날씨"):
        return 알림재료.outfit_text()
    return HELP


if not tg.MY_CHAT_ID and not OPEN_TO_ALL:
    raise SystemExit("⚠️  .env 에 MY_CHAT_ID 가 없어요. 1_채팅ID찾기.py 로 먼저 알아내요.")

me = tg.call("getMe")
tg.log(f"봇 켜짐: @{me['username']} / " + ("⚠️ 누구에게나 대답" if OPEN_TO_ALL else "🔒 나에게만 대답"))
print("   (끄려면 Ctrl + C)")

offset = None                       # 이미 읽은 메시지 다음 번호 (같은 메시지에 두 번 답하지 않게)
try:
    while True:
        params = {"timeout": 30}    # 새 메시지가 올 때까지 최대 30초 기다리며 물어봄 (자주 두드리지 않기)
        if offset:
            params["offset"] = offset
        for u in tg.call("getUpdates", params, wait=40):
            offset = u["update_id"] + 1
            msg = u.get("message")
            if not msg or "text" not in msg:
                continue
            chat_id = str(msg["chat"]["id"])
            who = msg["chat"].get("first_name", "?")
            if not OPEN_TO_ALL and chat_id != tg.MY_CHAT_ID:
                tg.log(f"🚫 모르는 사람 무시: {who} (채팅 ID {chat_id}) '{msg['text'][:20]}'")
                continue
            tg.log(f"📩 {who}: {msg['text'][:30]}")
            tg.send(chat_id, answer(msg["text"]))
            tg.log("📤 대답 보냄")
except KeyboardInterrupt:
    tg.log("봇 꺼짐 (Ctrl + C)")

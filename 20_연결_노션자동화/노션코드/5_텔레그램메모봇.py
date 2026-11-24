"""도전 미션: 텔레그램으로 보낸 메모가 노션 '학습기록'에 쌓이게 하기.

- 19번 텔레그램 도구(19_연결_텔레그램봇/봇코드/텔레그램도구.py)와 20번 노션 도구를 함께 써요.
- 토큰은 각자 폴더의 .env 에서 꺼내요 (19/.env 텔레그램, 20/.env 노션).
- 나(19/.env 의 MY_CHAT_ID)에게서 온 글만 받아요. 모르는 사람은 기록만 남기고 무시.

봇에게 이렇게 보내요
  /memo 오늘 노션 API 배움       ← 메모 저장
  /메모 오늘 노션 API 배움       ← 위와 같음
  그냥 글만 보내도 메모로 저장해요 (단, /start 같은 다른 명령은 도움말)

노션에 들어가는 모양
  제목 = 메모 앞부분(40자), 얻은 능력 = 메모 전체, 날짜 = 오늘, 키트 = '메모'

실행 (20 폴더에서): python3 노션코드/5_텔레그램메모봇.py      끄기: Ctrl + C
※ 19번 3_명령봇.py 와 동시에 켜지 마세요 (같은 우편함을 둘이 열면 편지를 나눠 가져요).
"""
import os
import sys
from datetime import date

import 노션도구 as nt

sys.path.insert(0, os.path.join(nt.FOLDER, "..", "19_연결_텔레그램봇", "봇코드"))
import 텔레그램도구 as tg  # noqa: E402

HELP = ("📝 메모 봇이에요. 보내는 글을 노션 '학습기록'에 저장해요.\n"
        "예) /memo 오늘 노션 API 배움   (그냥 글만 보내도 돼요)")


def memo_text(text):
    """메모로 저장할 글. 메모가 아니면 None."""
    text = text.strip()
    for cmd in ("/memo", "/메모"):
        if text.lower().startswith(cmd):
            rest = text[len(cmd):]
            if rest.startswith("@"):                  # '/memo@봇이름 내용' 모양이면 봇 이름 떼기
                rest = rest.split(" ", 1)[1] if " " in rest else ""
            return rest.strip() or None
    return None if text.startswith("/") else text


def save(memo):
    """노션 학습기록 표에 메모 한 장 추가. 노션 주소를 돌려준다."""
    page = nt.call("POST", "pages", {
        "parent": {"database_id": nt.database_id()},
        "properties": {
            "제목": {"title": [{"text": {"content": memo[:40]}}]},
            "날짜": {"date": {"start": date.today().isoformat()}},
            "키트": {"select": {"name": "메모"}},
            "얻은 능력": {"rich_text": [{"text": {"content": memo[:2000]}}]},
        },
    })
    return page["url"]


if not tg.MY_CHAT_ID:
    raise SystemExit("⚠️  19번 .env 에 MY_CHAT_ID 가 없어요.")

me = tg.call("getMe")
tg.log(f"메모봇 켜짐: @{me['username']} → 노션 학습기록 / 🔒 나에게만")
print("   (끄려면 Ctrl + C)")
offset = None
try:
    while True:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        for u in tg.call("getUpdates", params, wait=40):
            offset = u["update_id"] + 1
            msg = u.get("message")
            if not msg or "text" not in msg:
                continue
            chat_id = str(msg["chat"]["id"])
            if chat_id != tg.MY_CHAT_ID:
                tg.log(f"🚫 모르는 사람 무시: 채팅 ID {chat_id}")
                continue
            memo = memo_text(msg["text"])
            if not memo:
                tg.send(chat_id, HELP)
                continue
            url = save(memo)
            tg.log(f"📝 노션에 메모 저장: {memo[:30]}")
            tg.send(chat_id, f"📝 노션에 저장했어요!\n{memo[:40]}\n{url}")
except KeyboardInterrupt:
    tg.log("메모봇 꺼짐 (Ctrl + C)")

"""미션 2 준비 (+ 미션 5 재료): 내 봇에게 말을 건 사람들의 채팅 ID를 보여 주기.

- 봇은 "누구에게" 보낼지 알아야 해요. 그 주소가 채팅 ID(숫자)예요.
- 먼저 휴대폰에서 내 봇에게 아무 말이나 보낸 다음 실행하세요.
- 메시지를 보내지는 않아요. 받은 편지함(getUpdates)을 읽기만 해요.
- 찾은 숫자는 직접 .env 의 MY_CHAT_ID= 뒤에 넣어요.

실행 (19 폴더에서): python3 봇코드/1_채팅ID찾기.py
"""
import 텔레그램도구 as tg

me = tg.call("getMe")
print(f"🤖 내 봇: {me['first_name']} (@{me['username']})")

updates = tg.call("getUpdates")
people = {}
for u in updates:
    msg = u.get("message") or u.get("edited_message")
    if msg:
        chat = msg["chat"]
        name = chat.get("first_name") or chat.get("title") or "?"
        people[chat["id"]] = (name, msg.get("text", "(글 아닌 메시지)"))

if not people:
    print("📭 아직 받은 메시지가 없어요. 휴대폰에서 봇에게 '안녕'을 보내고 다시 실행해요.")
else:
    print(f"📬 최근 받은 메시지 {len(updates)}개, 보낸 사람 {len(people)}명")
    for chat_id, (name, text) in people.items():
        print(f"   채팅 ID {chat_id}  ← {name}: {text[:20]}")
    print("👉 내 이름 옆 숫자를 .env 의 MY_CHAT_ID= 뒤에 넣어요.")

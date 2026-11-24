"""미션 2: 봇이 나에게 '안녕하세요'를 보내게 하기.

- 보낼 곳은 .env 의 MY_CHAT_ID (1_채팅ID찾기.py 로 알아낸 내 번호)
- 진짜 메시지가 휴대폰에 가요.

실행 (19 폴더에서): python3 봇코드/2_안녕보내기.py
"""
import 텔레그램도구 as tg

if not tg.MY_CHAT_ID:
    raise SystemExit("⚠️  .env 에 MY_CHAT_ID 가 아직 없어요. 먼저 1_채팅ID찾기.py 를 실행해요.")

tg.send(tg.MY_CHAT_ID, "안녕하세요! 👋 맥에 사는 비서 봇이에요.")
tg.log("미션2: '안녕하세요' 보냄")

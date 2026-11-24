"""텔레그램과 대화하는 공용 도구 (다른 파일들이 불러 써요).

- 파이썬 기본 기능(urllib)만 써요. 새로 설치할 것 없음.
- 토큰과 내 채팅 ID는 19번 폴더의 .env 금고에서 꺼내요 (.gitignore로 GitHub 제외).
- 텔레그램이 "너무 많이 물어봐, N초 뒤에 와"(429)라고 하면, 그 시간만큼 기다렸다가 한 번만 다시 물어요.
- 오류 문장에 토큰이 섞여 나오지 않게 가려요.
"""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))          # 봇코드 폴더
FOLDER = os.path.dirname(HERE)                             # 19_연결_텔레그램봇 폴더
ENV_FILE = os.path.join(FOLDER, ".env")
OUT_DIR = os.path.join(FOLDER, "결과")


def load_env(path=ENV_FILE):
    values = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    name, value = line.split("=", 1)
                    values[name.strip()] = value.strip()
    return values


ENV = load_env()
TOKEN = ENV.get("TELEGRAM_BOT_TOKEN", "")
MY_CHAT_ID = ENV.get("MY_CHAT_ID", "")
if not MY_CHAT_ID.lstrip("-").isdigit():                   # 아직 '여기에_내_채팅_ID' 그대로면 빈칸 취급
    MY_CHAT_ID = ""


def hide(text):
    """글 속에 토큰이 있으면 <토큰>으로 바꾼다."""
    return str(text).replace(TOKEN, "<토큰>") if TOKEN else str(text)


def call(method, params=None, wait=40):
    """텔레그램 API 하나를 부르고 결과(result)를 돌려준다. 실패하면 이유를 알려 주고 멈춘다."""
    if ":" not in TOKEN:
        raise SystemExit("⚠️  .env 에 TELEGRAM_BOT_TOKEN 이 비어 있거나 모양이 이상해요.")
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = urlencode(params or {}).encode("utf-8")
    for attempt in (1, 2):
        try:
            with urlopen(Request(url, data=data), timeout=wait) as res:
                return json.loads(res.read().decode("utf-8"))["result"]
        except HTTPError as e:
            body = json.loads(e.read().decode("utf-8") or "{}")
            if e.code == 429 and attempt == 1:
                sec = body.get("parameters", {}).get("retry_after", 30)
                print(f"⏳ 텔레그램: 너무 자주 물어봤대요. {sec}초 기다렸다가 한 번만 다시 물어요...")
                time.sleep(sec + 1)
                continue
            raise SystemExit(f"❌ 텔레그램 오류 {e.code}: {hide(body.get('description', ''))}")
        except URLError as e:
            raise SystemExit(f"❌ 텔레그램에 연결하지 못했어요: {hide(e.reason)}")


def send(chat_id, text):
    """chat_id 에게 글을 보낸다. 텔레그램 한 번에 4096자까지라 넘으면 잘라 보낸다."""
    for i in range(0, len(text), 4000):
        call("sendMessage", {"chat_id": chat_id, "text": text[i:i + 4000]})


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log(line):
    """결과/봇기록.log 에 한 줄 남긴다 (화면에도 보여 줌)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    line = f"[{stamp()}] {hide(line)}"
    print(line)
    with open(os.path.join(OUT_DIR, "봇기록.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

"""노션과 대화하는 공용 도구 (다른 파일들이 불러 써요).

- 파이썬 기본 기능(urllib)만 써요. 새로 설치할 것 없음.
- 토큰과 데이터베이스 ID는 20번 폴더의 .env 금고에서 꺼내요 (.gitignore로 GitHub 제외).
- 노션 API 버전은 '2022-06-28'(오래 지원되는 안정판)을 써요.
- 오류 문장에 토큰이 섞여 나오지 않게 가려요.
"""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))       # 노션코드 폴더
FOLDER = os.path.dirname(HERE)                          # 20_연결_노션자동화 폴더
ENV_FILE = os.path.join(FOLDER, ".env")
OUT_DIR = os.path.join(FOLDER, "결과")
API = "https://api.notion.com/v1/"
VERSION = "2022-06-28"


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
TOKEN = ENV.get("NOTION_TOKEN", "")
DB_ID = ENV.get("NOTION_DATABASE_ID", "")
if "여기에" in DB_ID:                                    # 아직 예시 글자 그대로면 빈칸 취급
    DB_ID = ""


def hide(text):
    return str(text).replace(TOKEN, "<토큰>") if TOKEN else str(text)


def call(method, path, body=None):
    """노션 API 하나를 부르고 결과(JSON)를 돌려준다. 너무 자주 부르면(429) 잠깐 쉬었다 한 번 더."""
    if not TOKEN.startswith(("ntn_", "secret_")):
        raise SystemExit("⚠️  .env 의 NOTION_TOKEN 이 비어 있거나 모양이 이상해요 (ntn_ 로 시작).")
    headers = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION,
               "Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in (1, 2):
        try:
            with urlopen(Request(API + path, data=data, headers=headers, method=method), timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except HTTPError as e:
            info = json.loads(e.read().decode("utf-8") or "{}")
            if e.code == 429 and attempt == 1:
                sec = int(e.headers.get("Retry-After", "2"))
                print(f"⏳ 노션: 너무 빨라요. {sec}초 쉬었다가 한 번 더...")
                time.sleep(sec)
                continue
            raise SystemExit(f"❌ 노션 오류 {e.code} ({info.get('code', '')}): {hide(info.get('message', ''))}")
        except URLError as e:
            raise SystemExit(f"❌ 노션에 연결하지 못했어요: {hide(e.reason)}")


def find_database():
    """이 연결이 볼 수 있는 데이터베이스 목록 [(ID, 이름)] — .env 에 ID가 없을 때 찾기용."""
    res = call("POST", "search", {"filter": {"property": "object", "value": "database"}})
    out = []
    for db in res.get("results", []):
        name = "".join(t["plain_text"] for t in db.get("title", [])) or "(이름 없음)"
        out.append((db["id"].replace("-", ""), name))
    return out


def database_id():
    """.env 의 NOTION_DATABASE_ID, 없으면 볼 수 있는 데이터베이스가 딱 1개일 때 그것."""
    if DB_ID:
        return DB_ID
    found = find_database()
    if len(found) == 1:
        return found[0][0]
    raise SystemExit(f"⚠️  데이터베이스를 하나로 못 정했어요 (찾은 개수 {len(found)}). "
                     ".env 에 NOTION_DATABASE_ID 를 넣어 주세요.")

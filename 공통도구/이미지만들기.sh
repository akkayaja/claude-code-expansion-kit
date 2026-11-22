#!/bin/bash
# ChatGPT(Codex CLI)로 그림 한 장을 만들어 원하는 이름으로 저장해요.
# 사용법:  공통도구/이미지만들기.sh "그림 설명" 저장할이름.png
# ⚠️ 내 ChatGPT 요금제 사용량을 써요. 한 번 실행 = 그림 1장.
set -e
PROMPT="$1"
OUT="${2:-image.png}"
if [ -z "$PROMPT" ]; then echo '사용법: 이미지만들기.sh "그림 설명" 저장할이름.png'; exit 1; fi
CODEX="$(command -v codex || echo /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex)"
MARK="$(mktemp)"
echo "🎨 ChatGPT에 그림을 요청하는 중... (1~2분 걸려요)"
"$CODEX" exec --skip-git-repo-check "이미지 생성 도구로 그림을 딱 한 장 만들어 줘. 다른 파일 작업은 하지 마. 그림 설명: $PROMPT" > /dev/null 2>&1
NEW="$(find "$HOME/.codex/generated_images" -name '*.png' -newer "$MARK" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)"
rm -f "$MARK"
if [ -z "$NEW" ]; then echo "❌ 그림을 찾지 못했어요. 00_시작하기/README.md 의 '문제가 생기면'을 보세요."; exit 1; fi
cp "$NEW" "$OUT"
echo "✅ 저장했어요: $OUT"

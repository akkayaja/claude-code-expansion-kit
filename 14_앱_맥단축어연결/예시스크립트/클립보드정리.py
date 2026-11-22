# 클립보드에 복사된 글에서 빈 줄과 겹친 공백을 정리해 다시 클립보드에 넣어요.
import re, subprocess
text = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
clean = "\n".join(ln for ln in lines if ln)
subprocess.run(["pbcopy"], input=clean, text=True)
print(f"정리했어요: {len(text)}자 → {len(clean)}자")

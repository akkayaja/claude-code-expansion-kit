# 바탕화면에 오늘 날짜 폴더(예: 2026-11-22)를 만들고 Finder로 열어요.
import datetime, os, subprocess
folder = os.path.expanduser(f"~/Desktop/{datetime.date.today():%Y-%m-%d}")
os.makedirs(folder, exist_ok=True)
subprocess.run(["open", folder])
print("만들었어요:", folder)

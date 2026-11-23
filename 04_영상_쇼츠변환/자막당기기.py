# 자막 시간표를 원하는 만큼 앞으로 당기고, 쇼츠 길이 밖의 자막은 빼는 스크립트
# (1초도 안 남는 자투리 자막은 깜빡이기만 하니 뺀다)
# 사용법: python3 자막당기기.py 원본.srt 결과.srt 시작초 끝초
import re, sys

원본, 결과, 시작, 끝 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])

def 초로(t):  # "00:00:06,100" → 6.1
    h, m, s = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def 글자로(x):  # 6.1 → "00:00:06,100"
    ms = round(x * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

블록들 = open(원본, encoding="utf-8").read().strip().split("\n\n")
남은것 = []
for 블록 in 블록들:
    줄 = 블록.strip().split("\n")
    a, b = re.findall(r"\d+:\d+:\d+,\d+", 줄[1])
    s, e = 초로(a) - 시작, 초로(b) - 시작
    if e <= 0 or s >= 끝 - 시작:   # 쇼츠 구간 밖이면 빼기
        continue
    s, e = max(s, 0), min(e, 끝 - 시작)
    if e - s < 1:                 # 잘리고 1초도 안 남으면 빼기
        continue
    남은것.append(f"{len(남은것) + 1}\n{글자로(s)} --> {글자로(e)}\n" + "\n".join(x.strip() for x in 줄[2:]))

open(결과, "w", encoding="utf-8").write("\n\n".join(남은것) + "\n")
print(f"자막 {len(블록들)}개 중 {len(남은것)}개를 {시작}초만큼 당겨서 저장했어요 → {결과}")

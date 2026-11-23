"""구간 목록(CSV)을 읽어서 세로 쇼츠를 한 번에 여러 개 만드는 스크립트.

하는 일 (한 줄마다):
    1. 원본에서 그 구간만 자르기
    2. 1080x1920 세로로 바꾸기 (위아래 흐린 배경)
    3. 자막 시간표를 구간 시작만큼 당겨서 크고 굵게 입히기
    4. 맨 위에 제목 띠 넣기

사용법 (04_영상_쇼츠변환 폴더에서):
    python3 쇼츠뽑기.py 구간목록.csv

CSV 칸: 이름,시작,끝,제목   (제목의 / 는 줄바꿈)
"""
import csv
import os
import re
import subprocess
import sys

FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
FFPROBE = os.path.expanduser("~/.local/bin/ffprobe")
원본영상 = "media/가로영상.mp4"
원본자막 = "../02_영상_자막자동생성/결과/강의샘플.srt"
결과폴더 = "결과/쇼츠3개"

자막모양 = ("FontName=Apple SD Gothic Neo,FontSize=16,Bold=1,Outline=3,"
           "MarginV=60,MarginL=20,MarginR=20")

제목틀 = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: 제목,Apple SD Gothic Neo,90,&H00FFFFFF,&H00FFFFFF,&H0023A6F5,&H0023A6F5,1,0,0,0,100,100,0,0,3,24,0,8,60,60,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,{끝},제목,,0,0,0,,{글}
"""


def 초로(t):  # "00:00:06,100" → 6.1
    h, m, s = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def 글자로(x):  # 6.1 → "00:00:06,100"
    ms = round(x * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def 자막_당기기(시작, 끝, 저장할곳):
    """원본 자막을 구간에 맞게 당기고, 구간 밖·1초 미만 자투리는 뺀다. 남은 개수를 돌려준다."""
    블록들 = open(원본자막, encoding="utf-8").read().strip().split("\n\n")
    남은것 = []
    for 블록 in 블록들:
        줄 = 블록.strip().split("\n")
        a, b = re.findall(r"\d+:\d+:\d+,\d+", 줄[1])
        s, e = max(초로(a) - 시작, 0), min(초로(b) - 시작, 끝 - 시작)
        if e - s < 1:  # 구간 밖이거나 1초도 안 남으면 빼기
            continue
        남은것.append(f"{len(남은것) + 1}\n{글자로(s)} --> {글자로(e)}\n"
                    + "\n".join(x.strip() for x in 줄[2:]))
    open(저장할곳, "w", encoding="utf-8").write("\n\n".join(남은것) + "\n")
    return len(남은것)


def 길이들(파일):
    """화면·소리 길이를 ffprobe로 잰다."""
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "stream=codec_type,width,height,duration",
         "-of", "compact", 파일], capture_output=True, text=True, check=True).stdout
    return out.strip().replace("\n", "  ")


def 쇼츠_만들기(이름, 시작, 끝, 제목):
    자막파일 = f"{결과폴더}/{이름}.srt"
    제목파일 = f"{결과폴더}/{이름}_제목.ass"
    출력 = f"{결과폴더}/{이름}.mp4"

    자막수 = 자막_당기기(시작, 끝, 자막파일)
    h, rest = divmod(끝 - 시작, 3600)
    m, s = divmod(rest, 60)
    open(제목파일, "w", encoding="utf-8").write(
        제목틀.format(끝=f"{int(h)}:{int(m):02}:{s:05.2f}", 글=제목.replace("/", r"\N")))

    그림 = (
        "[0:v]split[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[bg];"
        "[b]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"subtitles={자막파일}:force_style='{자막모양}',"
        f"ass={제목파일}[v]"
    )
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-ss", str(시작), "-to", str(끝), "-i", 원본영상,
         "-filter_complex", 그림, "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-c:a", "aac", 출력], check=True)
    print(f"✅ {출력}  (자막 {자막수}개)  {길이들(출력)}")


if __name__ == "__main__":
    목록 = sys.argv[1] if len(sys.argv) > 1 else "구간목록.csv"
    os.makedirs(결과폴더, exist_ok=True)
    with open(목록, encoding="utf-8") as f:
        줄들 = list(csv.DictReader(f))
    print(f"구간 {len(줄들)}개를 쇼츠로 만들어요.")
    for 줄 in 줄들:
        쇼츠_만들기(줄["이름"], float(줄["시작"]), float(줄["끝"]), 줄["제목"])
    print("끝!")

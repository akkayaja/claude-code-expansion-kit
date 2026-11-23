"""무음 구간을 찾아 잘라 낸 영상을 만드는 스크립트.

사용법:
    python3 무음컷.py 입력.mp4 출력.mp4 [남길초]

    남길초: 말 앞뒤로 남겨 둘 여유(초). 기본 0 = 무음을 전부 잘라 냄.
"""
import os
import re
import subprocess
import sys

FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
FFPROBE = os.path.expanduser("~/.local/bin/ffprobe")
NOISE = "-30dB"   # 이보다 작은 소리는 '조용함'
MIN_SILENCE = 1.0  # 이 시간(초) 이상 이어져야 무음으로 인정


def 길이(파일):
    """영상 전체 길이(초)를 ffprobe로 잰다."""
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", 파일],
        capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def 무음_찾기(파일):
    """silencedetect로 (시작, 끝) 무음 구간 목록을 만든다."""
    log = subprocess.run(
        [FFMPEG, "-hide_banner", "-nostats", "-i", 파일,
         "-af", f"silencedetect=noise={NOISE}:d={MIN_SILENCE}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(starts, ends))


def 남길_구간(무음들, 전체, 여유):
    """무음 구간 사이사이의 '말하는 구간' 목록을 만든다. 여유만큼 앞뒤로 넓힌다."""
    구간들, 앞 = [], 0.0
    for 시작, 끝 in 무음들:
        if 시작 > 앞:
            구간들.append((max(0.0, 앞 - 여유), min(전체, 시작 + 여유)))
        앞 = 끝
    if 앞 < 전체:
        구간들.append((max(0.0, 앞 - 여유), 전체))
    return [(a, b) for a, b in 구간들 if b - a > 0.05]


def 자르기(입력, 출력, 구간들):
    """각 구간을 trim으로 오려 concat으로 이어 붙인다."""
    조각, 연결 = [], ""
    for i, (a, b) in enumerate(구간들):
        조각.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}]")
        조각.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{i}]")
        연결 += f"[v{i}][a{i}]"
    필터 = ";".join(조각) + f";{연결}concat=n={len(구간들)}:v=1:a=1[v][a]"
    subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", 입력,
         "-filter_complex", 필터, "-map", "[v]", "-map", "[a]", 출력],
        check=True)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    입력, 출력 = sys.argv[1], sys.argv[2]
    여유 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

    전체 = 길이(입력)
    무음들 = 무음_찾기(입력)
    구간들 = 남길_구간(무음들, 전체, 여유)

    print(f"무음 구간 {len(무음들)}개를 찾았어요 (여유 {여유}초)")
    for i, (a, b) in enumerate(구간들, 1):
        print(f"  남길 구간 {i}: {a:6.2f}초 ~ {b:6.2f}초")

    os.makedirs(os.path.dirname(출력) or ".", exist_ok=True)
    자르기(입력, 출력, 구간들)

    결과 = 길이(출력)
    print(f"완료: {출력}")
    print(f"길이: {전체:.2f}초 → {결과:.2f}초 ({(1 - 결과 / 전체) * 100:.1f}% 줄었어요)")


if __name__ == "__main__":
    main()

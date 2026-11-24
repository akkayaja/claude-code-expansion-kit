// 맥에 내장된 글자 인식(Apple Vision)으로 사진 속 글자를 읽어 줄마다 출력해요.
// 사용법: swift OCR코드/글자읽기.swift images/영수증_01.png
import Foundation
import Vision
import AppKit

let 경로 = CommandLine.arguments[1]
guard let 그림 = NSImage(contentsOfFile: 경로),
      let cg = 그림.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("사진을 열 수 없어요: \(경로)"); exit(1)
}

let 요청 = VNRecognizeTextRequest()
요청.recognitionLevel = .accurate          // 느려도 정확하게
요청.recognitionLanguages = ["ko-KR", "en-US"] // 한국어 + 영어/숫자
요청.usesLanguageCorrection = true

try VNImageRequestHandler(cgImage: cg).perform([요청])

// 위에서 아래 순서로 정렬해서 한 줄씩 출력 (Vision은 아래쪽이 0이라 큰 값이 위)
let 줄들 = (요청.results ?? []).sorted { $0.boundingBox.midY > $1.boundingBox.midY }
for 줄 in 줄들 {
    if let 글 = 줄.topCandidates(1).first { print(글.string) }
}

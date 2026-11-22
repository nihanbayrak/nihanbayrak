// Writes a grayscale person mask for an image using Apple's on-device Vision segmentation.
import Foundation
import Vision
import CoreImage

let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1]), output = URL(fileURLWithPath: args[2])
let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
try VNImageRequestHandler(url: input).perform([request])
guard let mask = request.results?.first?.pixelBuffer else { fatalError("no person found") }
let image = CIImage(cvPixelBuffer: mask)
let ctx = CIContext()
try ctx.writePNGRepresentation(of: image, to: output, format: .L8, colorSpace: CGColorSpaceCreateDeviceGray())
print("mask", CVPixelBufferGetWidth(mask), CVPixelBufferGetHeight(mask))

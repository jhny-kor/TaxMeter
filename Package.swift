// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "TaxMeterCore",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(name: "TaxMeterCore", targets: ["TaxMeterCore"])
    ],
    targets: [
        .target(name: "TaxMeterCore"),
        .testTarget(name: "TaxMeterCoreTests", dependencies: ["TaxMeterCore"])
    ]
)

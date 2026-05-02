import SwiftUI

enum TaxMeterFormat {
    private static let formatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.maximumFractionDigits = 2
        return formatter
    }()

    static func decimal(_ value: Decimal) -> String {
        formatter.string(from: NSDecimalNumber(decimal: value)) ?? "0"
    }
}

extension Color {
    static let taxMeterBackground = Color(.systemGroupedBackground)
    static let taxMeterCard = Color(.secondarySystemGroupedBackground)
    static let taxMeterMuted = Color(.tertiarySystemGroupedBackground)
    static let taxMeterBorder = Color(.separator).opacity(0.22)
    static let taxMeterInk = Color(red: 0.09, green: 0.11, blue: 0.16)
    static let taxMeterGreen = Color(red: 0.10, green: 0.52, blue: 0.32)
    static let taxMeterAmber = Color(red: 0.72, green: 0.44, blue: 0.05)
    static let taxMeterRed = Color(red: 0.76, green: 0.16, blue: 0.18)
}

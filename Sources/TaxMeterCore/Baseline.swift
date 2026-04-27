import Foundation

public enum BaselineCategory: String, CaseIterable, Codable, Sendable {
    case financialIncome
    case healthInsurance
    case deductions
    case comprehensiveIncome
    case pension
    case subscription
    case business
    case investment
    case youthPolicy
    case grant
}

public struct Baseline: Identifiable, Codable, Equatable, Sendable {
    public let id: UUID
    public let title: String
    public let category: BaselineCategory
    public let threshold: Decimal
    public let unit: String

    public init(
        id: UUID = UUID(),
        title: String,
        category: BaselineCategory,
        threshold: Decimal,
        unit: String
    ) {
        self.id = id
        self.title = title
        self.category = category
        self.threshold = threshold
        self.unit = unit
    }
}

public struct BaselineDistance: Equatable, Sendable {
    public let baseline: Baseline
    public let currentValue: Decimal
    public let distance: Decimal

    public var isExceeded: Bool {
        currentValue > baseline.threshold
    }

    public var progressRatio: Double {
        guard baseline.threshold > .zero else { return 1 }
        let currentNumber = NSDecimalNumber(decimal: currentValue)
        let thresholdNumber = NSDecimalNumber(decimal: baseline.threshold)
        guard thresholdNumber != .zero else { return 1 }
        let ratio = currentNumber.dividing(by: thresholdNumber).doubleValue
        return min(max(ratio, 0), 2)
    }

    public init(baseline: Baseline, currentValue: Decimal, distance: Decimal) {
        self.baseline = baseline
        self.currentValue = currentValue
        self.distance = distance
    }
}

import Foundation

public struct BaselineEngine {
    public init() {}

    public func evaluate(
        baselines: [Baseline],
        currentValues: [UUID: Decimal]
    ) -> [BaselineDistance] {
        baselines.map { baseline in
            let current = currentValues[baseline.id] ?? .zero
            let distance = baseline.threshold - current
            return BaselineDistance(baseline: baseline, currentValue: current, distance: distance)
        }
        .sorted { lhs, rhs in
            absDecimal(lhs.distance) < absDecimal(rhs.distance)
        }
    }

    private func absDecimal(_ value: Decimal) -> Decimal {
        value < .zero ? value * -1 : value
    }
}

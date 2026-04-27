import Foundation
import TaxMeterCore

final class DashboardViewModel: ObservableObject {
    @Published private(set) var distances: [BaselineDistance] = []
    @Published var values: [UUID: String] = [:]

    private let baselines: [Baseline]
    private let engine: BaselineEngine

    var topRisks: [BaselineDistance] {
        Array(distances.prefix(3))
    }

    var exceededCount: Int {
        distances.filter(\.isExceeded).count
    }

    var completedInputCount: Int {
        values.values.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }.count
    }

    var totalBaselineCount: Int {
        baselines.count
    }

    init(
        baselines: [Baseline] = BaselineCatalog.mvpTop15,
        engine: BaselineEngine = BaselineEngine()
    ) {
        self.baselines = baselines
        self.engine = engine
        self.values = Dictionary(uniqueKeysWithValues: baselines.map { ($0.id, "") })
        recalculate()
    }

    func updateValue(for baselineID: UUID, text: String) {
        values[baselineID] = text
        recalculate()
    }

    func inputValue(for baselineID: UUID) -> String {
        values[baselineID] ?? ""
    }

    private func recalculate() {
        let parsed: [UUID: Decimal] = values.reduce(into: [:]) { partial, element in
            let sanitized = element.value.replacingOccurrences(of: ",", with: "")
            partial[element.key] = Decimal(string: sanitized) ?? .zero
        }
        distances = engine.evaluate(baselines: baselines, currentValues: parsed)
    }
}

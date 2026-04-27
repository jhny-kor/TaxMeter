import SwiftUI
import TaxMeterCore

struct BaselineCardView: View {
    let item: BaselineDistance
    let inputValue: String
    let onEdit: (String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(item.baseline.title)
                .font(.headline)
            Text("기준값: \(format(item.baseline.threshold))\(item.baseline.unit)")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            TextField("현재값 입력", text: Binding(
                get: { inputValue },
                set: { onEdit($0) }
            ))
            .textFieldStyle(.roundedBorder)
            .keyboardType(.numberPad)

            HStack {
                Label(statusText, systemImage: item.isExceeded ? "exclamationmark.triangle.fill" : "checkmark.circle.fill")
                    .foregroundStyle(item.isExceeded ? .red : .green)
                Spacer()
                Text("거리: \(format(item.distance))\(item.baseline.unit)")
                    .font(.caption)
            }

            ProgressView(value: item.progressRatio)
                .tint(item.isExceeded ? .red : .blue)
        }
        .padding()
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

    private var statusText: String {
        item.isExceeded ? "기준 초과" : "안전 구간"
    }

    private func format(_ value: Decimal) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        let number = NSDecimalNumber(decimal: value)
        return formatter.string(from: number) ?? "0"
    }
}

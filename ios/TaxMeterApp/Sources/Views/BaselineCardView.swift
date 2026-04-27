import SwiftUI
import TaxMeterCore

struct BaselineCardView: View {
    let item: BaselineDistance
    let inputValue: String
    var isHighlighted = false
    let onEdit: (String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 12) {
                CategoryIconView(category: item.baseline.category)

                VStack(alignment: .leading, spacing: 4) {
                    Text(item.baseline.title)
                        .font(.system(.headline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)

                    Text(categoryText)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Spacer(minLength: 10)

                StatusBadgeView(
                    text: statusText,
                    systemImage: statusIcon,
                    tint: statusColor
                )
            }

            HStack(spacing: 8) {
                MetricPillView(title: "현재", value: "\(format(item.currentValue))\(item.baseline.unit)")
                MetricPillView(title: "기준", value: "\(format(item.baseline.threshold))\(item.baseline.unit)")
                MetricPillView(title: item.isExceeded ? "초과" : "남음", value: distanceText)
            }

            VStack(alignment: .leading, spacing: 8) {
                ProgressMeterView(
                    progress: item.progressRatio,
                    tint: statusColor
                )

                HStack(spacing: 8) {
                    Image(systemName: "number")
                        .font(.caption)
                        .foregroundStyle(.secondary)

                    TextField("현재값 입력", text: Binding(
                        get: { inputValue },
                        set: { onEdit($0) }
                    ))
                    .keyboardType(.decimalPad)
                    .font(.system(.subheadline, design: .rounded))
                    .monospacedDigit()
                }
                .padding(.vertical, 10)
                .padding(.horizontal, 12)
                .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8))
            }
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 10))
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(isHighlighted ? statusColor.opacity(0.35) : Color.taxMeterBorder, lineWidth: 1)
        )
    }

    private var statusText: String {
        if item.isExceeded {
            return "초과"
        }
        return item.progressRatio >= 0.85 ? "근접" : "여유"
    }

    private var statusIcon: String {
        if item.isExceeded {
            return "exclamationmark"
        }
        return item.progressRatio >= 0.85 ? "clock" : "checkmark"
    }

    private var statusColor: Color {
        if item.isExceeded {
            return .taxMeterRed
        }
        return item.progressRatio >= 0.85 ? .taxMeterAmber : .taxMeterGreen
    }

    private var distanceText: String {
        "\(format(absDecimal(item.distance)))\(item.baseline.unit)"
    }

    private var categoryText: String {
        switch item.baseline.category {
        case .financialIncome:
            return "금융소득"
        case .healthInsurance:
            return "건강보험"
        case .deductions:
            return "공제"
        case .comprehensiveIncome:
            return "종합소득"
        case .pension:
            return "연금"
        case .subscription:
            return "청약"
        case .business:
            return "사업자"
        case .investment:
            return "투자"
        case .youthPolicy:
            return "청년정책"
        case .grant:
            return "지원금"
        }
    }

    private func format(_ value: Decimal) -> String {
        TaxMeterFormat.decimal(value)
    }

    private func absDecimal(_ value: Decimal) -> Decimal {
        value < .zero ? value * -1 : value
    }
}

struct StatusBadgeView: View {
    let text: String
    let systemImage: String
    let tint: Color

    var body: some View {
        Label(text, systemImage: systemImage)
            .font(.caption.weight(.semibold))
            .labelStyle(.titleAndIcon)
            .foregroundStyle(tint)
            .padding(.vertical, 6)
            .padding(.horizontal, 8)
            .background(tint.opacity(0.12), in: Capsule())
    }
}

private struct CategoryIconView: View {
    let category: BaselineCategory

    var body: some View {
        Image(systemName: systemImage)
            .font(.system(size: 15, weight: .semibold))
            .foregroundStyle(Color.taxMeterInk)
            .frame(width: 34, height: 34)
            .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8))
    }

    private var systemImage: String {
        switch category {
        case .financialIncome:
            return "banknote"
        case .healthInsurance:
            return "cross.case"
        case .deductions:
            return "doc.text.magnifyingglass"
        case .comprehensiveIncome:
            return "sum"
        case .pension:
            return "calendar.badge.clock"
        case .subscription:
            return "house"
        case .business:
            return "briefcase"
        case .investment:
            return "chart.xyaxis.line"
        case .youthPolicy:
            return "person.crop.circle.badge.checkmark"
        case .grant:
            return "giftcard"
        }
    }
}

private struct MetricPillView: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title)
                .font(.caption2)
                .foregroundStyle(.secondary)

            Text(value)
                .font(.system(.caption, design: .rounded, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)
                .lineLimit(1)
                .minimumScaleFactor(0.65)
                .monospacedDigit()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 8)
        .padding(.horizontal, 10)
        .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8))
    }
}

private struct ProgressMeterView: View {
    let progress: Double
    let tint: Color

    var body: some View {
        GeometryReader { proxy in
            ZStack(alignment: .leading) {
                Capsule()
                    .fill(Color.taxMeterMuted)

                Capsule()
                    .fill(tint)
                    .frame(width: proxy.size.width * min(max(progress, 0), 1))
            }
        }
        .frame(height: 8)
        .accessibilityLabel("기준선 진행률")
        .accessibilityValue("\(Int(min(max(progress, 0), 1) * 100))퍼센트")
    }
}

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

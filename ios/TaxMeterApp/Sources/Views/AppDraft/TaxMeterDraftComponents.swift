import SwiftUI

struct TaxMeterAppIconView: View {
    var size: CGFloat = 82

    var body: some View {
        Image("TaxMeterIcon")
            .resizable()
            .interpolation(.high)
            .clipShape(RoundedRectangle(cornerRadius: size * 0.22, style: .continuous))
            .frame(width: size, height: size)
            .shadow(color: Color.taxMeterInk.opacity(0.12), radius: 18, x: 0, y: 10)
            .accessibilityLabel("TaxMeter 앱 아이콘")
    }
}

struct DraftSectionHeaderView: View {
    let title: String
    let caption: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.system(.headline, design: .rounded, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)

            Text(caption)
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

struct DraftMetricBoxView: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption2)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.system(.subheadline, design: .rounded, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.72)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 10)
        .padding(.horizontal, 12)
        .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8, style: .continuous))
    }
}

extension LinearGradient {
    static var taxMeterPastelBackground: LinearGradient {
        LinearGradient(
            colors: [
                Color(red: 0.93, green: 0.97, blue: 1.00),
                Color(red: 0.98, green: 0.93, blue: 0.97),
                Color(red: 0.99, green: 0.96, blue: 0.86)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}

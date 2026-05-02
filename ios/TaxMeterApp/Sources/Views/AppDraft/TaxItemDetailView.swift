import SwiftUI

struct TaxItemDetailView: View {
    let item: DraftTaxItem

    private var exceededCriteria: [DraftCriterion] {
        item.criteria.filter { $0.state == .exceeded }
    }

    private var nearCriteria: [DraftCriterion] {
        item.criteria.filter { $0.state == .near }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                DetailHeroView(item: item)

                VStack(alignment: .leading, spacing: 12) {
                    DraftSectionHeaderView(
                        title: "기준선 위치",
                        caption: "100% 선을 기준으로 예시 값이 어느 지점에 있는지 표시합니다."
                    )

                    ForEach(item.criteria) { criterion in
                        CriterionProgressCardView(criterion: criterion)
                    }
                }

                DetailAnalysisView(
                    exceededCriteria: exceededCriteria,
                    nearCriteria: nearCriteria
                )
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 18)
        }
        .background(Color.taxMeterBackground)
        .navigationTitle(item.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct DetailHeroView: View {
    let item: DraftTaxItem

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 14) {
                ZStack {
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .fill(item.tint.opacity(0.35))

                    Image(systemName: item.symbolName)
                        .font(.system(size: 28, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)
                }
                .frame(width: 60, height: 60)

                VStack(alignment: .leading, spacing: 6) {
                    Text(item.title)
                        .font(.system(.title3, design: .rounded, weight: .bold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text(item.subtitle)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                }

                Spacer(minLength: 0)
            }

            Text(item.description)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }
}

private struct CriterionProgressCardView: View {
    let criterion: DraftCriterion

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .top, spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(criterion.title)
                        .font(.system(.headline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text(criterion.note)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer(minLength: 10)

                StatusBadgeView(
                    text: criterion.state.label,
                    systemImage: criterion.state.iconName,
                    tint: criterion.state.color
                )
            }

            HStack(spacing: 10) {
                DraftMetricBoxView(title: "예시 값", value: "\(criterion.percent)%")
                DraftMetricBoxView(title: "기준선", value: "100%")
                DraftMetricBoxView(title: "샘플 입력", value: formattedValue)
            }

            BaselineMarkerTrackView(criterion: criterion)
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(criterion.state.color.opacity(0.28), lineWidth: 1)
        )
    }

    private var formattedValue: String {
        if criterion.unit == "비율" {
            let value = NSDecimalNumber(decimal: criterion.currentValue)
                .multiplying(by: 100)
                .decimalValue
            return "\(TaxMeterFormat.decimal(value))%"
        }
        return "\(TaxMeterFormat.decimal(criterion.currentValue))\(criterion.unit)"
    }
}

private struct BaselineMarkerTrackView: View {
    let criterion: DraftCriterion

    private var clampedRatio: Double {
        min(max(criterion.ratio, 0), 1.18)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            GeometryReader { proxy in
                let markerX = proxy.size.width * CGFloat(clampedRatio / 1.18)
                let baselineX = proxy.size.width * CGFloat(1 / 1.18)

                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(Color.taxMeterMuted)
                        .frame(height: 8)
                        .position(x: proxy.size.width / 2, y: 34)

                    Rectangle()
                        .fill(Color.taxMeterInk.opacity(0.38))
                        .frame(width: 2, height: 26)
                        .position(x: baselineX, y: 34)

                    Text("100%")
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(.secondary)
                        .position(x: baselineX, y: 8)

                    Text("\(criterion.percent)%")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(.white)
                        .padding(.vertical, 4)
                        .padding(.horizontal, 7)
                        .background(criterion.state.color, in: RoundedRectangle(cornerRadius: 5, style: .continuous))
                        .position(x: min(max(markerX, 22), proxy.size.width - 22), y: 58)
                }
            }
            .frame(height: 72)

            HStack {
                Text("0%")
                Spacer()
                Text("기준선")
                Spacer()
                Text("초과")
            }
            .font(.caption2)
            .foregroundStyle(.secondary)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(criterion.title) 기준선 위치")
        .accessibilityValue("\(criterion.percent)퍼센트, \(criterion.state.label)")
    }
}

private struct DetailAnalysisView: View {
    let exceededCriteria: [DraftCriterion]
    let nearCriteria: [DraftCriterion]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("샘플 분석", systemImage: "text.magnifyingglass")
                .font(.system(.headline, design: .rounded, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)

            Text(resultText)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }

    private var resultText: String {
        if !exceededCriteria.isEmpty {
            let names = exceededCriteria.map(\.title).joined(separator: ", ")
            return "\(names) 항목이 샘플 기준선을 초과했습니다. 실제 입력 연결 뒤에는 관련 증빙과 신고 필요 여부를 먼저 확인합니다."
        }

        if !nearCriteria.isEmpty {
            let names = nearCriteria.map(\.title).joined(separator: ", ")
            return "\(names) 항목이 샘플 기준선에 근접했습니다. 실제 입력 연결 뒤에는 추가 소득이나 지출 변동을 다시 확인합니다."
        }

        return "현재 샘플 기준으로 초과된 기준선은 없습니다."
    }
}

#Preview {
    NavigationStack {
        TaxItemDetailView(item: TaxMeterDraftData.taxItems[0])
    }
}

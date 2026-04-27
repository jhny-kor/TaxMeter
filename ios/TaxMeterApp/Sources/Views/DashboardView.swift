import SwiftUI
import TaxMeterCore

struct DashboardView: View {
    @ObservedObject var viewModel: DashboardViewModel

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    DashboardHeaderView()

                    DashboardSummaryView(
                        nearest: viewModel.topRisks.first,
                        exceededCount: viewModel.exceededCount,
                        completedInputCount: viewModel.completedInputCount,
                        totalCount: viewModel.totalBaselineCount
                    )

                    VStack(alignment: .leading, spacing: 12) {
                        SectionHeaderView(
                            title: "가까운 기준선",
                            caption: "지금 입력값 기준으로 먼저 확인할 항목"
                        )

                        ForEach(viewModel.topRisks, id: \.baseline.id) { distance in
                            BaselineCardView(
                                item: distance,
                                inputValue: viewModel.inputValue(for: distance.baseline.id),
                                isHighlighted: true,
                                onEdit: { viewModel.updateValue(for: distance.baseline.id, text: $0) }
                            )
                        }
                    }

                    VStack(alignment: .leading, spacing: 12) {
                        SectionHeaderView(
                            title: "전체 기준선",
                            caption: "세금, 공제, 보험, 정책 자격을 한 화면에서 비교"
                        )

                        ForEach(viewModel.distances, id: \.baseline.id) { distance in
                            BaselineCardView(
                                item: distance,
                                inputValue: viewModel.inputValue(for: distance.baseline.id),
                                onEdit: { viewModel.updateValue(for: distance.baseline.id, text: $0) }
                            )
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 18)
            }
            .background(Color.taxMeterBackground)
            .navigationTitle("TaxMeter")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

private struct DashboardHeaderView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 10) {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(.white)
                    .frame(width: 34, height: 34)
                    .background(Color.taxMeterInk, in: RoundedRectangle(cornerRadius: 8))

                Text("TaxMeter")
                    .font(.system(.headline, design: .rounded, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
            }

            VStack(alignment: .leading, spacing: 6) {
                Text("내 현재 위치와 제도 기준선의 거리")
                    .font(.system(.title2, design: .rounded, weight: .bold))
                    .foregroundStyle(Color.taxMeterInk)

                Text("소득, 공제, 보험 기준을 입력값 기준으로 정렬해 위험한 항목부터 보여줍니다.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

private struct DashboardSummaryView: View {
    let nearest: BaselineDistance?
    let exceededCount: Int
    let completedInputCount: Int
    let totalCount: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .top, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("가장 가까운 기준")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundStyle(.secondary)

                    Text(nearest?.baseline.title ?? "기준선 없음")
                        .font(.system(.title3, design: .rounded, weight: .bold))
                        .foregroundStyle(Color.taxMeterInk)
                        .lineLimit(2)
                        .minimumScaleFactor(0.85)

                    if let nearest {
                        Text(distanceCaption(for: nearest))
                            .font(.subheadline)
                            .foregroundStyle(nearest.isExceeded ? Color.taxMeterRed : .secondary)
                    }
                }

                Spacer(minLength: 12)

                StatusBadgeView(
                    text: exceededCount == 0 ? "정상" : "\(exceededCount)개 초과",
                    systemImage: exceededCount == 0 ? "checkmark" : "exclamationmark",
                    tint: exceededCount == 0 ? Color.taxMeterGreen : Color.taxMeterRed
                )
            }

            HStack(spacing: 10) {
                SummaryMetricView(title: "입력", value: "\(completedInputCount)/\(totalCount)")
                SummaryMetricView(title: "초과", value: "\(exceededCount)")
                SummaryMetricView(title: "기준선", value: "\(totalCount)")
            }
        }
        .padding(18)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 10))
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }

    private func format(_ value: Decimal) -> String {
        TaxMeterFormat.decimal(value)
    }

    private func distanceCaption(for item: BaselineDistance) -> String {
        let absoluteDistance = item.distance < .zero ? item.distance * -1 : item.distance
        let suffix = item.isExceeded ? "초과" : "남음"
        return "\(format(absoluteDistance))\(item.baseline.unit) \(suffix)"
    }
}

private struct SummaryMetricView: View {
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
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 10)
        .padding(.horizontal, 12)
        .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8))
    }
}

private struct SectionHeaderView: View {
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
        }
    }
}

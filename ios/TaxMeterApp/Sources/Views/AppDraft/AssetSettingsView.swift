import SwiftUI

struct AssetSettingsView: View {
    @State private var assets = TaxMeterDraftData.assetItems

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                SettingsHeroView()

                VStack(alignment: .leading, spacing: 12) {
                    DraftSectionHeaderView(
                        title: "개인 자산 입력",
                        caption: "직접 확인한 금액만 입력하세요. TaxMeter는 금융기관에서 자동으로 가져오지 않습니다."
                    )

                    ForEach($assets) { $asset in
                        AssetInputCardView(asset: $asset)
                    }
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 18)
        }
        .background(Color.taxMeterBackground)
        .navigationTitle("자산 설정")
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct SettingsHeroView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("자산 확인 경로", systemImage: "gearshape")
                .font(.system(.headline, design: .rounded, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)

            Text("은행, 증권사, 홈택스, 정부24 등에서 직접 확인한 자료를 기준으로 자산 금액을 적어둡니다.")
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

private struct AssetInputCardView: View {
    @Binding var asset: DraftAssetItem

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: asset.symbolName)
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .frame(width: 38, height: 38)
                    .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8, style: .continuous))

                VStack(alignment: .leading, spacing: 4) {
                    Text(asset.title)
                        .font(.system(.headline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text(asset.guidance)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            HStack(spacing: 10) {
                Image(systemName: "wonsign")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                TextField("금액 입력", text: $asset.amount)
                    .keyboardType(.numberPad)
                    .font(.system(.subheadline, design: .rounded))
                    .monospacedDigit()
            }
            .padding(.vertical, 11)
            .padding(.horizontal, 12)
            .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8, style: .continuous))

            Link(destination: asset.url) {
                Label("확인 경로 열기", systemImage: "arrow.up.right.square")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color.taxMeterInk)
            }
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }
}

#Preview {
    NavigationStack {
        AssetSettingsView()
    }
}

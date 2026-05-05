import SwiftUI

struct AssetSettingsView: View {
    @State private var selectedCategoryID = TaxMeterDraftData.categories.first?.id ?? "category.tax-credits"

    private var selectedCategory: DraftCategory? {
        TaxMeterDraftData.categories.first { $0.id == selectedCategoryID } ?? TaxMeterDraftData.categories.first
    }

    private var filteredItems: [DraftTaxItem] {
        guard let selectedCategory else { return [] }
        return TaxMeterDraftData.taxItems.filter { $0.categoryID == selectedCategory.id }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                SettingsHeroView()

                CategoryTabsView(
                    categories: TaxMeterDraftData.categories,
                    selectedCategoryID: $selectedCategoryID
                )

                if let selectedCategory {
                    VStack(alignment: .leading, spacing: 12) {
                        DraftSectionHeaderView(
                            title: "\(selectedCategory.title) 확인 설정",
                            caption: "입력 전에 확인해야 할 정보와 항목별 공식 확인 경로입니다."
                        )

                        ForEach(filteredItems) { item in
                            SettingsTaxCheckCardView(item: item)
                        }
                    }
                } else {
                    SettingsUnavailableCardView()
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 18)
        }
        .background(Color.taxMeterBackground)
        .navigationTitle("확인 설정")
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct SettingsUnavailableCardView: View {
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "exclamationmark.triangle")
                .foregroundStyle(Color.taxMeterAmber)
                .padding(.top, 1)

            Text("tax ontology 리소스를 읽지 못해 확인 설정을 표시할 수 없습니다.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}

private struct SettingsHeroView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("확인 정보 설정", systemImage: "gearshape")
                .font(.system(.headline, design: .rounded, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)

            Text("TaxMeter는 금융기관이나 다른 앱에서 자동으로 자료를 가져오지 않습니다. 아래 항목은 tax ontology의 필요 입력과 공식 출처를 기준으로 확인 경로를 보여줍니다.")
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

private struct SettingsTaxCheckCardView: View {
    let item: DraftTaxItem

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: item.symbolName)
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .frame(width: 38, height: 38)
                    .background(item.tint.opacity(0.28), in: RoundedRectangle(cornerRadius: 8, style: .continuous))

                VStack(alignment: .leading, spacing: 4) {
                    Text(item.title)
                        .font(.system(.headline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text(item.description)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            SettingsInfoSectionView(
                title: "확인 필요 정보",
                systemImage: "square.and.pencil",
                items: item.requiredInputs
            )

            SettingsLinkSectionView(links: item.checkLinks)
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }
}

private struct SettingsInfoSectionView: View {
    let title: String
    let systemImage: String
    let items: [DraftInfoItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(title, systemImage: systemImage)
                .font(.caption.weight(.bold))
                .foregroundStyle(Color.taxMeterInk)

            ForEach(items) { item in
                SettingsInfoRowView(item: item)
            }
        }
    }
}

private struct SettingsInfoRowView: View {
    let item: DraftInfoItem

    var body: some View {
        HStack(alignment: .top, spacing: 9) {
            Image(systemName: item.symbolName)
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk.opacity(0.7))
                .frame(width: 20, height: 20)
                .background(Color.taxMeterMuted, in: Circle())

            VStack(alignment: .leading, spacing: 2) {
                Text(item.title)
                    .font(.system(.subheadline, design: .rounded, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)

                Text(item.detail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

private struct SettingsLinkSectionView: View {
    let links: [DraftCheckLink]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("확인 경로", systemImage: "link")
                .font(.caption.weight(.bold))
                .foregroundStyle(Color.taxMeterInk)

            ForEach(links) { link in
                Link(destination: link.url) {
                    SettingsLinkRowView(link: link)
                }
                .buttonStyle(.plain)
            }
        }
    }
}

private struct SettingsLinkRowView: View {
    let link: DraftCheckLink

    var body: some View {
        HStack(alignment: .top, spacing: 9) {
            Image(systemName: link.symbolName)
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk.opacity(0.7))
                .frame(width: 20, height: 20)
                .background(Color.taxMeterMuted, in: Circle())

            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 5) {
                    Text(link.title)
                        .font(.system(.subheadline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)

                    Image(systemName: "arrow.up.right")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(Color.taxMeterInk.opacity(0.58))
                }

                Text("\(link.publisher) · \(link.detail)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 0)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 10)
        .background(Color.taxMeterMuted.opacity(0.78), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
    }
}

#Preview {
    NavigationStack {
        AssetSettingsView()
    }
}

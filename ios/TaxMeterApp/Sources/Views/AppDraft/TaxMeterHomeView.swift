import SwiftUI

struct TaxMeterHomeView: View {
    @State private var selectedCategoryID = TaxMeterDraftData.categories.first?.id ?? "category.tax-credits"

    private let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16)
    ]

    private var selectedCategory: DraftCategory? {
        TaxMeterDraftData.categories.first { $0.id == selectedCategoryID } ?? TaxMeterDraftData.categories.first
    }

    private var filteredItems: [DraftTaxItem] {
        guard let selectedCategory else { return [] }
        return TaxMeterDraftData.taxItems.filter { $0.categoryID == selectedCategory.id }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    HomeHeaderView()

                    CategoryTabsView(
                        categories: TaxMeterDraftData.categories,
                        selectedCategoryID: $selectedCategoryID
                    )

                    if let selectedCategory {
                        DraftSectionHeaderView(
                            title: selectedCategory.title,
                            caption: "항목별 확인 가능 정보와 기준선을 선택해 살펴봅니다."
                        )

                        LazyVGrid(columns: columns, spacing: 16) {
                            ForEach(filteredItems) { item in
                                NavigationLink(value: item) {
                                    DraftTaxItemTileView(item: item)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    } else {
                        OntologyUnavailableCardView()
                    }

                    GuidanceNoticeView()
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 18)
            }
            .background(LinearGradient.taxMeterPastelBackground.ignoresSafeArea())
            .toolbar(.hidden, for: .navigationBar)
            .navigationDestination(for: DraftTaxItem.self) { item in
                TaxItemDetailView(item: item)
            }
        }
    }
}

private struct OntologyUnavailableCardView: View {
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "exclamationmark.triangle")
                .foregroundStyle(Color.taxMeterAmber)
                .padding(.top, 1)

            Text("번들에 포함된 tax ontology를 읽지 못했습니다. 앱 리소스에 korea-tax-ontology-2026.json이 포함되어야 합니다.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .background(.white.opacity(0.72), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}

private struct HomeHeaderView: View {
    var body: some View {
        HStack(alignment: .center, spacing: 14) {
            TaxMeterAppIconView(size: 58)

            VStack(alignment: .leading, spacing: 5) {
                Text("세금 기준선 보기")
                    .font(.system(.title2, design: .rounded, weight: .bold))
                    .foregroundStyle(Color.taxMeterInk)

                Text("온톨로지 기준선과 확인 경로를 항목별로 봅니다.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 10)

            NavigationLink {
                AssetSettingsView()
            } label: {
                Image(systemName: "gearshape")
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .frame(width: 38, height: 38)
                    .background(.white.opacity(0.76), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .stroke(.white.opacity(0.8), lineWidth: 1)
                    )
            }
            .buttonStyle(.plain)
            .accessibilityLabel("확인 설정")
        }
    }
}

struct CategoryTabsView: View {
    let categories: [DraftCategory]
    @Binding var selectedCategoryID: String

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(categories) { category in
                    Button {
                        withAnimation(.snappy(duration: 0.2)) {
                            selectedCategoryID = category.id
                        }
                    } label: {
                        Text(category.title)
                            .font(.system(.subheadline, design: .rounded, weight: .semibold))
                            .foregroundStyle(selectedCategoryID == category.id ? .white : Color.taxMeterInk)
                            .padding(.vertical, 9)
                            .padding(.horizontal, 14)
                            .background(
                                selectedCategoryID == category.id ? Color.taxMeterInk : .white.opacity(0.72),
                                in: Capsule()
                            )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.vertical, 2)
        }
        .accessibilityLabel("항목 종류 탭")
    }
}

private struct DraftTaxItemTileView: View {
    let item: DraftTaxItem

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ZStack {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [item.tint.opacity(0.88), .white.opacity(0.78)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )

                Image(systemName: item.symbolName)
                    .font(.system(size: 30, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .symbolRenderingMode(.hierarchical)

                VStack {
                    HStack {
                        Spacer()

                        Text("\(item.criteria.count)")
                            .font(.caption2.weight(.bold))
                            .foregroundStyle(Color.taxMeterInk)
                            .frame(width: 24, height: 24)
                            .background(.white.opacity(0.76), in: Circle())
                    }

                    Spacer()
                }
                .padding(8)
            }
            .frame(height: 82)

            VStack(alignment: .leading, spacing: 4) {
                Text(item.title)
                    .font(.system(.headline, design: .rounded, weight: .bold))
                    .foregroundStyle(Color.taxMeterInk)
                    .lineLimit(1)
                    .minimumScaleFactor(0.82)

                Text(item.subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .fixedSize(horizontal: false, vertical: true)

                Text(item.mainCheckSummary)
                    .font(.caption2.weight(.medium))
                    .foregroundStyle(Color.taxMeterInk.opacity(0.62))
                    .lineLimit(1)
                    .minimumScaleFactor(0.78)

                Text("\(item.checkLinks.count)개 확인 경로")
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(Color.taxMeterInk.opacity(0.5))
                    .lineLimit(1)
            }
        }
        .padding(12)
        .aspectRatio(1, contentMode: .fit)
        .background(.white.opacity(0.78), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.white.opacity(0.75), lineWidth: 1)
        )
        .shadow(color: Color.taxMeterInk.opacity(0.06), radius: 14, x: 0, y: 8)
    }
}

private struct GuidanceNoticeView: View {
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "info.circle")
                .foregroundStyle(Color.taxMeterAmber)
                .padding(.top, 1)

            Text("카테고리와 항목은 tax ontology 노드와 공식 출처를 기준으로 구성됩니다. 실제 계산에는 사용자가 확인해 저장한 입력값만 사용합니다.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .background(.white.opacity(0.72), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}

#Preview {
    TaxMeterHomeView()
}

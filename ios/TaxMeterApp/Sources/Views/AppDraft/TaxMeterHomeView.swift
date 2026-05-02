import SwiftUI

struct TaxMeterHomeView: View {
    @State private var selectedCategoryID = TaxMeterDraftData.categories.first?.id ?? "income"

    private let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16)
    ]

    private var selectedCategory: DraftCategory {
        TaxMeterDraftData.categories.first { $0.id == selectedCategoryID } ?? TaxMeterDraftData.categories[0]
    }

    private var filteredItems: [DraftTaxItem] {
        TaxMeterDraftData.taxItems.filter { $0.categoryID == selectedCategoryID }
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

                    DraftSectionHeaderView(
                        title: selectedCategory.title,
                        caption: "항목을 선택하면 예시 기준선 위치와 초과 표시 방식을 확인합니다."
                    )

                    LazyVGrid(columns: columns, spacing: 16) {
                        ForEach(filteredItems) { item in
                            NavigationLink(value: item) {
                                DraftTaxItemTileView(item: item)
                            }
                            .buttonStyle(.plain)
                        }
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

private struct HomeHeaderView: View {
    var body: some View {
        HStack(alignment: .center, spacing: 14) {
            TaxMeterAppIconView(size: 58)

            VStack(alignment: .leading, spacing: 5) {
                Text("세금 기준선 보기")
                    .font(.system(.title2, design: .rounded, weight: .bold))
                    .foregroundStyle(Color.taxMeterInk)

                Text("예시 값이 어느 기준선에 가까운지 항목별로 미리 봅니다.")
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
            .accessibilityLabel("개인 자산 설정")
        }
    }
}

private struct CategoryTabsView: View {
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
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
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

            Text("현재 화면은 샘플 데이터로 구성된 UI 초안입니다. 실제 서비스에서는 사용자가 직접 확인해 입력한 자료만 기준으로 사용합니다.")
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

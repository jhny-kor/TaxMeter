import SwiftUI

struct TaxItemDetailView: View {
    let item: DraftTaxItem
    @State private var criterionInputs: [String: String]
    @State private var savedCriterionInputs: [String: String]
    @State private var saveStatus: DetailSaveStatus = .clean
    @State private var showsResetConfirmation = false

    init(item: DraftTaxItem) {
        self.item = item
        let savedValues = Dictionary(
            uniqueKeysWithValues: item.criteria.map { ($0.id, CriterionInputStore.value(for: $0)) }
        )
        _criterionInputs = State(
            initialValue: savedValues
        )
        _savedCriterionInputs = State(
            initialValue: savedValues
        )
    }

    private var hasUnsavedChanges: Bool {
        criterionInputs != savedCriterionInputs
    }

    private var editedCriteria: [DraftCriterion] {
        item.criteria.map { criterion in
            guard let inputText = criterionInputs[criterion.id],
                  let currentValue = CriterionInputParser.currentValue(from: inputText, unit: criterion.unit)
            else {
                return criterion
            }

            return criterion.replacingCurrentValue(currentValue)
        }
    }

    private var exceededCriteria: [DraftCriterion] {
        editedCriteria.filter { $0.state == .exceeded }
    }

    private var nearCriteria: [DraftCriterion] {
        editedCriteria.filter { $0.state == .near }
    }

    private func inputBinding(for criterion: DraftCriterion) -> Binding<String> {
        Binding(
            get: { criterionInputs[criterion.id] ?? criterion.editableInputValue },
            set: { newValue in
                var nextInputs = criterionInputs
                nextInputs[criterion.id] = newValue
                criterionInputs = nextInputs
                saveStatus = nextInputs == savedCriterionInputs ? .clean : .editing
            }
        )
    }

    private func saveInputs() {
        for criterion in item.criteria {
            let value = criterionInputs[criterion.id] ?? criterion.editableInputValue
            CriterionInputStore.set(value, for: criterion.id)
        }

        savedCriterionInputs = criterionInputs
        saveStatus = .saved
    }

    private func resetInputs() {
        for criterion in item.criteria {
            CriterionInputStore.remove(for: criterion.id)
        }

        let defaultInputs = Dictionary(
            uniqueKeysWithValues: item.criteria.map { ($0.id, $0.editableInputValue) }
        )
        criterionInputs = defaultInputs
        savedCriterionInputs = defaultInputs
        saveStatus = .reset
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                DetailHeroView(item: item)

                VStack(alignment: .leading, spacing: 12) {
                    DraftSectionHeaderView(
                        title: "기준선 위치",
                        caption: "100% 선을 기준으로 직접 입력한 값이 어느 지점에 있는지 표시합니다."
                    )

                    if editedCriteria.isEmpty {
                        NoCriterionCardView()
                    } else {
                        ForEach(editedCriteria) { criterion in
                            CriterionProgressCardView(
                                criterion: criterion,
                                inputText: inputBinding(for: criterion)
                            )
                        }

                        DetailSaveBarView(
                            status: saveStatus,
                            hasUnsavedChanges: hasUnsavedChanges,
                            saveAction: saveInputs,
                            resetAction: { showsResetConfirmation = true }
                        )
                    }
                }

                if !editedCriteria.isEmpty {
                    DetailAnalysisView(
                        exceededCriteria: exceededCriteria,
                        nearCriteria: nearCriteria
                    )
                }

                DetailInfoSectionView(
                    title: "필요 입력",
                    caption: "계산 전에 사용자가 직접 확인해 입력해야 하는 값입니다.",
                    systemImage: "square.and.pencil",
                    items: item.requiredInputs
                )

                DetailInfoSectionView(
                    title: "확인 자료",
                    caption: "입력값을 대조할 때 필요한 자료와 증빙입니다.",
                    systemImage: "doc.text.magnifyingglass",
                    items: item.evidenceItems
                )

                DetailInfoSectionView(
                    title: "경계선 체크",
                    caption: "기준선 근처에서 반드시 다시 확인할 조건입니다.",
                    systemImage: "checklist",
                    items: item.boundaryChecks
                )

                DetailLinkSectionView(links: item.checkLinks)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 18)
        }
        .background(Color.taxMeterBackground)
        .navigationTitle(item.title)
        .navigationBarTitleDisplayMode(.inline)
        .confirmationDialog(
            "입력값 초기화",
            isPresented: $showsResetConfirmation,
            titleVisibility: .visible
        ) {
            Button("초기화", role: .destructive, action: resetInputs)
            Button("취소", role: .cancel) {}
        } message: {
            Text("저장된 입력값을 삭제하고 ontology 기본값으로 되돌립니다.")
        }
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

                    Text("OpenTax: \(item.ontologyID)")
                        .font(.caption2.weight(.medium))
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.72)
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

private enum DetailSaveStatus {
    case clean
    case editing
    case saved
    case reset

    var title: String {
        switch self {
        case .clean:
            return "저장됨"
        case .editing:
            return "미저장 변경"
        case .saved:
            return "저장 완료"
        case .reset:
            return "초기값 복원"
        }
    }

    var detail: String {
        switch self {
        case .clean:
            return "저장된 입력값으로 기준선을 계산합니다."
        case .editing:
            return "값을 저장해야 다음 진입 때도 유지됩니다."
        case .saved:
            return "현재 화면의 입력값을 기기에 저장했습니다."
        case .reset:
            return "저장된 입력값을 지우고 온톨로지 기본값으로 돌렸습니다."
        }
    }

    var color: Color {
        switch self {
        case .clean, .saved:
            return .taxMeterGreen
        case .editing:
            return .taxMeterAmber
        case .reset:
            return .taxMeterInk
        }
    }

    var iconName: String {
        switch self {
        case .clean:
            return "checkmark.circle"
        case .editing:
            return "pencil.circle"
        case .saved:
            return "checkmark.seal"
        case .reset:
            return "arrow.counterclockwise.circle"
        }
    }
}

private struct DetailSaveBarView: View {
    let status: DetailSaveStatus
    let hasUnsavedChanges: Bool
    let saveAction: () -> Void
    let resetAction: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: status.iconName)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(status.color)
                    .frame(width: 26, height: 26)
                    .background(status.color.opacity(0.13), in: RoundedRectangle(cornerRadius: 7, style: .continuous))

                VStack(alignment: .leading, spacing: 3) {
                    Text(status.title)
                        .font(.system(.subheadline, design: .rounded, weight: .bold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text(status.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer(minLength: 0)
            }

            HStack(spacing: 10) {
                Button(action: saveAction) {
                    Label("저장", systemImage: "checkmark.circle")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color.taxMeterInk)
                .disabled(!hasUnsavedChanges)

                Button(action: resetAction) {
                    Label("초기화", systemImage: "arrow.counterclockwise")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .tint(Color.taxMeterInk)
            }
            .font(.system(.subheadline, design: .rounded, weight: .semibold))
        }
        .padding(14)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(status.color.opacity(0.28), lineWidth: 1)
        )
    }
}

private struct NoCriterionCardView: View {
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "text.magnifyingglass")
                .font(.system(size: 16, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk)
                .frame(width: 26, height: 26)
                .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 7, style: .continuous))

            VStack(alignment: .leading, spacing: 4) {
                Text("숫자 기준선 없음")
                    .font(.system(.headline, design: .rounded, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)

                Text("이 온톨로지 노드는 구조화된 금액·비율 기준이 없어서, 필요 입력과 공식 확인 경로를 중심으로 점검합니다.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
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

private struct CriterionProgressCardView: View {
    let criterion: DraftCriterion
    @Binding var inputText: String

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
                DraftMetricBoxView(title: "현재 위치", value: "\(criterion.percent)%")
                DraftMetricBoxView(title: "기준값", value: criterion.formattedBaselineValue)
                DraftMetricBoxView(title: "입력값", value: criterion.formattedCurrentValue)
            }

            BaselineMarkerTrackView(criterion: criterion)

            HStack(spacing: 10) {
                Image(systemName: "pencil")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)

                TextField("값 직접 입력", text: $inputText)
                    .keyboardType(.decimalPad)
                    .font(.system(.subheadline, design: .rounded))
                    .monospacedDigit()

                Text(criterion.unit == "비율" ? "%" : criterion.unit)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            }
            .padding(.vertical, 11)
            .padding(.horizontal, 12)
            .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 8, style: .continuous))
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(criterion.state.color.opacity(0.28), lineWidth: 1)
        )
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
            Label("입력 분석", systemImage: "text.magnifyingglass")
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
            return "\(names) 항목이 기준선을 초과했습니다. 관련 증빙과 신고 필요 여부를 먼저 확인합니다."
        }

        if !nearCriteria.isEmpty {
            let names = nearCriteria.map(\.title).joined(separator: ", ")
            return "\(names) 항목이 기준선에 근접했습니다. 추가 소득이나 지출 변동을 다시 확인합니다."
        }

        return "현재 입력 기준으로 초과된 기준선은 없습니다."
    }
}

private struct DetailInfoSectionView: View {
    let title: String
    let caption: String
    let systemImage: String
    let items: [DraftInfoItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: systemImage)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .frame(width: 26, height: 26)
                    .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 7, style: .continuous))

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

            VStack(alignment: .leading, spacing: 12) {
                ForEach(items) { item in
                    DetailInfoRowView(item: item)
                }
            }
            .padding(.leading, 2)
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }
}

private struct DetailInfoRowView: View {
    let item: DraftInfoItem

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: item.symbolName)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk.opacity(0.72))
                .frame(width: 22, height: 22)
                .background(Color.taxMeterMuted, in: Circle())

            VStack(alignment: .leading, spacing: 3) {
                Text(item.title)
                    .font(.system(.subheadline, design: .rounded, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .fixedSize(horizontal: false, vertical: true)

                Text(item.detail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

private struct DetailLinkSectionView: View {
    let links: [DraftCheckLink]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: "link")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(Color.taxMeterInk)
                    .frame(width: 26, height: 26)
                    .background(Color.taxMeterMuted, in: RoundedRectangle(cornerRadius: 7, style: .continuous))

                VStack(alignment: .leading, spacing: 4) {
                    Text("확인 경로")
                        .font(.system(.headline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text("입력값을 확인할 수 있는 공식 자료와 서비스입니다.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                ForEach(links) { link in
                    Link(destination: link.url) {
                        DetailLinkRowView(link: link)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.leading, 2)
        }
        .padding(16)
        .background(Color.taxMeterCard, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.taxMeterBorder, lineWidth: 1)
        )
    }
}

private struct DetailLinkRowView: View {
    let link: DraftCheckLink

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: link.symbolName)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(Color.taxMeterInk.opacity(0.72))
                .frame(width: 22, height: 22)
                .background(Color.taxMeterMuted, in: Circle())

            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 5) {
                    Text(link.title)
                        .font(.system(.subheadline, design: .rounded, weight: .semibold))
                        .foregroundStyle(Color.taxMeterInk)
                        .fixedSize(horizontal: false, vertical: true)

                    Image(systemName: "arrow.up.right")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(Color.taxMeterInk.opacity(0.56))
                }

                Text("\(link.publisher) · \(link.detail)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 0)
        }
    }
}

private enum CriterionInputParser {
    static func currentValue(from text: String, unit: String) -> Decimal? {
        let normalized = text
            .replacingOccurrences(of: ",", with: "")
            .replacingOccurrences(of: "원", with: "")
            .replacingOccurrences(of: "%", with: "")
            .replacingOccurrences(of: "세", with: "")
            .replacingOccurrences(of: "건", with: "")
            .trimmingCharacters(in: .whitespacesAndNewlines)

        guard !normalized.isEmpty,
              let value = Decimal(string: normalized, locale: Locale(identifier: "en_US_POSIX"))
        else {
            return nil
        }

        if unit == "비율" {
            return value / Decimal(100)
        }

        return value
    }
}

private enum CriterionInputStore {
    static func value(for criterion: DraftCriterion) -> String {
        UserDefaults.standard.string(forKey: key(for: criterion.id)) ?? criterion.editableInputValue
    }

    static func set(_ value: String, for criterionID: String) {
        UserDefaults.standard.set(value, forKey: key(for: criterionID))
    }

    static func remove(for criterionID: String) {
        UserDefaults.standard.removeObject(forKey: key(for: criterionID))
    }

    private static func key(for criterionID: String) -> String {
        "taxmeter.draft.criterion.\(criterionID)"
    }
}

#Preview {
    NavigationStack {
        TaxItemDetailView(item: TaxMeterDraftData.taxItems[0])
    }
}

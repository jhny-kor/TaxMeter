import Foundation
import SwiftUI

struct DraftCategory: Identifiable, Hashable {
    let id: String
    let title: String
}

struct DraftTaxItem: Identifiable, Hashable {
    let id: String
    let categoryID: String
    let title: String
    let subtitle: String
    let description: String
    let ontologyID: String
    let symbolName: String
    let tint: Color
    let criteria: [DraftCriterion]
    let requiredInputs: [DraftInfoItem]
    let evidenceItems: [DraftInfoItem]
    let boundaryChecks: [DraftInfoItem]
    let checkLinks: [DraftCheckLink]

    var mainCheckSummary: String {
        let summary = requiredInputs
            .prefix(2)
            .map(\.title)
            .joined(separator: " · ")

        return summary.isEmpty ? "공식 출처 확인" : summary
    }
}

struct DraftInfoItem: Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let symbolName: String
}

struct DraftCheckLink: Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let publisher: String
    let url: URL
    let symbolName: String
}

struct DraftCriterion: Identifiable, Hashable {
    let id: String
    let title: String
    let currentValue: Decimal
    let baselineValue: Decimal
    let unit: String
    let note: String

    var ratio: Double {
        guard baselineValue > .zero else { return 0 }
        let current = NSDecimalNumber(decimal: currentValue)
        let baseline = NSDecimalNumber(decimal: baselineValue)
        return current.dividing(by: baseline).doubleValue
    }

    var percent: Int {
        Int((ratio * 100).rounded())
    }

    var state: DraftCriterionState {
        if ratio > 1 {
            return .exceeded
        }
        if ratio >= 0.9 {
            return .near
        }
        return .normal
    }

    var formattedCurrentValue: String {
        formatted(currentValue)
    }

    var formattedBaselineValue: String {
        formatted(baselineValue)
    }

    var editableInputValue: String {
        if unit == "비율" {
            let percentValue = NSDecimalNumber(decimal: currentValue)
                .multiplying(by: 100)
                .decimalValue
            return TaxMeterFormat.decimal(percentValue)
        }

        return TaxMeterFormat.decimal(currentValue)
    }

    func replacingCurrentValue(_ value: Decimal) -> DraftCriterion {
        DraftCriterion(
            id: id,
            title: title,
            currentValue: value,
            baselineValue: baselineValue,
            unit: unit,
            note: note
        )
    }

    private func formatted(_ value: Decimal) -> String {
        if unit == "비율" {
            let percentValue = NSDecimalNumber(decimal: value)
                .multiplying(by: 100)
                .decimalValue
            return "\(TaxMeterFormat.decimal(percentValue))%"
        }

        return "\(TaxMeterFormat.decimal(value))\(unit)"
    }
}

enum DraftCriterionState: Hashable {
    case normal
    case near
    case exceeded

    var label: String {
        switch self {
        case .normal:
            return "정상"
        case .near:
            return "근접"
        case .exceeded:
            return "초과"
        }
    }

    var color: Color {
        switch self {
        case .normal:
            return .taxMeterGreen
        case .near:
            return .taxMeterAmber
        case .exceeded:
            return .taxMeterRed
        }
    }

    var iconName: String {
        switch self {
        case .normal:
            return "checkmark"
        case .near:
            return "clock"
        case .exceeded:
            return "exclamationmark"
        }
    }
}

enum TaxMeterDraftData {
    private static let store = DraftOntologyStore.load()

    static var categories: [DraftCategory] {
        store.categories
    }

    static var taxItems: [DraftTaxItem] {
        store.taxItems
    }
}

private struct DraftOntologyStore {
    let categories: [DraftCategory]
    let taxItems: [DraftTaxItem]

    private static let rootCategoryIDs = [
        "category.tax-credits",
        "deduction.other-income",
        "tax.income",
        "tax.income.capital-gains",
        "tax.value-added",
        "category.policy-supports",
        "category.eligibility-rules",
        "category.life-incomes"
    ]

    static func load(bundle: Bundle = .main) -> DraftOntologyStore {
        guard let export = loadExport(bundle: bundle) else {
            return DraftOntologyStore(categories: [], taxItems: [])
        }

        let nodesByID = Dictionary(uniqueKeysWithValues: export.items.map { ($0.id, $0) })
        let categories = rootCategoryIDs.compactMap { categoryID -> DraftCategory? in
            guard let node = nodesByID[categoryID] else { return nil }
            return DraftCategory(id: node.id, title: node.title)
        }

        let items = categories.flatMap { category in
            (nodesByID[category.id]?.children ?? []).compactMap { childID -> DraftTaxItem? in
                guard let node = nodesByID[childID],
                      isDisplayableItem(node),
                      !rootCategoryIDs.contains(node.id)
                else {
                    return nil
                }

                return makeTaxItem(
                    from: node,
                    categoryID: category.id,
                    categoryTitle: category.title,
                    nodesByID: nodesByID
                )
            }
        }

        return DraftOntologyStore(categories: categories, taxItems: items)
    }

    private static func loadExport(bundle: Bundle) -> DraftOntologyExport? {
        guard let url = bundle.url(forResource: "korea-tax-ontology-2026", withExtension: "json"),
              let data = try? Data(contentsOf: url)
        else {
            return nil
        }

        return try? JSONDecoder().decode(DraftOntologyExport.self, from: data)
    }

    private static func isDisplayableItem(_ node: DraftOntologyNode) -> Bool {
        node.type != "category" && node.type != "source"
    }

    private static func makeTaxItem(
        from node: DraftOntologyNode,
        categoryID: String,
        categoryTitle: String,
        nodesByID: [String: DraftOntologyNode]
    ) -> DraftTaxItem {
        let criteria = makeCriteria(for: node)
        let sourceNodes = referencedSourceNodes(for: node, nodesByID: nodesByID)

        return DraftTaxItem(
            id: node.id,
            categoryID: categoryID,
            title: node.title,
            subtitle: subtitle(for: node, categoryTitle: categoryTitle, criteriaCount: criteria.count),
            description: node.description ?? "\(node.title) 온톨로지 항목입니다.",
            ontologyID: node.id,
            symbolName: symbolName(for: node),
            tint: tint(for: node.id),
            criteria: criteria,
            requiredInputs: requiredInputs(for: node),
            evidenceItems: evidenceItems(for: node, sourceNodes: sourceNodes),
            boundaryChecks: boundaryChecks(for: node),
            checkLinks: checkLinks(for: node, sourceNodes: sourceNodes)
        )
    }

    private static func subtitle(for node: DraftOntologyNode, categoryTitle: String, criteriaCount: Int) -> String {
        let typeTitle = localizedType(node.type)
        if criteriaCount > 0 {
            return "\(typeTitle) · 기준 \(criteriaCount)개"
        }
        return "\(categoryTitle) · 공식 확인"
    }

    private static func makeCriteria(for node: DraftOntologyNode) -> [DraftCriterion] {
        (node.criteria ?? []).enumerated().flatMap { index, criterion in
            baselineValues(for: criterion).map { baseline in
                DraftCriterion(
                    id: "\(node.id).criterion.\(index).\(baseline.suffix)",
                    title: baseline.title,
                    currentValue: 0,
                    baselineValue: baseline.value,
                    unit: baseline.unit,
                    note: noteText(for: criterion, baselineLabel: baseline.label)
                )
            }
        }
    }

    private static func baselineValues(for criterion: DraftOntologyCriterion) -> [DraftCriterionBaseline] {
        var baselines: [DraftCriterionBaseline] = []
        let baseTitle = criterion.label ?? criterion.basis ?? "기준"

        if let value = criterion.thresholdKrwMax {
            baselines.append(.init(suffix: "threshold-max", title: baseTitle, label: "상한", value: value, unit: "원"))
        }

        if let value = criterion.thresholdKrwMin, criterion.thresholdKrwMax == nil {
            baselines.append(.init(suffix: "threshold-min", title: "\(baseTitle) 하한", label: "하한", value: value, unit: "원"))
        }

        if let value = criterion.limitKrw {
            baselines.append(.init(suffix: "limit", title: "\(baseTitle) 한도", label: "한도", value: value, unit: "원"))
        }

        if let value = criterion.deductionKrw {
            baselines.append(.init(suffix: "deduction", title: "\(baseTitle) 공제액", label: "공제액", value: value, unit: "원"))
        }

        if let value = criterion.maxAmountKrw {
            baselines.append(.init(suffix: "max-amount", title: "\(baseTitle) 최대금액", label: "최대금액", value: value, unit: "원"))
        }

        if let value = criterion.ageMax {
            baselines.append(.init(suffix: "age-max", title: baseTitle, label: "나이 상한", value: value, unit: "세"))
        }

        if let value = criterion.medianIncomePercentMax {
            baselines.append(.init(suffix: "median-income", title: baseTitle, label: "중위소득 비율", value: value / 100, unit: "비율"))
        }

        if baselines.isEmpty, let value = criterion.ratePercent {
            baselines.append(.init(suffix: "rate", title: "\(baseTitle) \(criterion.rateLabel ?? "율")", label: "비율", value: value / 100, unit: "비율"))
        }

        if baselines.isEmpty, let value = criterion.ratePercentMax {
            baselines.append(.init(suffix: "rate-max", title: "\(baseTitle) 최대율", label: "최대율", value: value / 100, unit: "비율"))
        }

        return baselines
    }

    private static func noteText(for criterion: DraftOntologyCriterion, baselineLabel: String) -> String {
        [
            criterion.basis.map { "basis: \($0)" },
            criterion.condition.map { "condition: \($0)" },
            criterion.rateLabel.flatMap { label in criterion.ratePercent.map { "\(label): \(TaxMeterFormat.decimal($0))%" } },
            criterion.benefit.map { "benefit: \($0)" },
            criterion.note.map { "note: \($0)" },
            criterion.amountFormula.map { "formula: \($0)" },
            "baseline: \(baselineLabel)"
        ]
        .compactMap { $0 }
        .joined(separator: " · ")
    }

    private static func requiredInputs(for node: DraftOntologyNode) -> [DraftInfoItem] {
        let criteria = node.criteria ?? []
        let inputs = criteria.prefix(5).enumerated().map { index, criterion in
            DraftInfoItem(
                id: "\(node.id).input.\(index)",
                title: criterion.basis ?? criterion.label ?? "기준 확인",
                detail: criterion.basisLookup ?? criterion.basisDefinition ?? criterion.condition ?? node.description ?? "온톨로지 criterion 기준을 확인합니다.",
                symbolName: symbolName(forBasis: criterion.basisCategory)
            )
        }

        if !inputs.isEmpty {
            return inputs
        }

        return [
            DraftInfoItem(
                id: "\(node.id).input.description",
                title: "적용 대상 확인",
                detail: node.description ?? "\(node.title) 적용 여부를 공식 출처에서 확인합니다.",
                symbolName: "text.magnifyingglass"
            ),
            DraftInfoItem(
                id: "\(node.id).input.sources",
                title: "공식 출처 확인",
                detail: "온톨로지의 source_urls와 source 노드에 연결된 자료를 확인합니다.",
                symbolName: "link"
            )
        ]
    }

    private static func evidenceItems(
        for node: DraftOntologyNode,
        sourceNodes: [DraftOntologyNode]
    ) -> [DraftInfoItem] {
        let evidence = sourceNodes.prefix(4).enumerated().map { index, source in
            DraftInfoItem(
                id: "\(node.id).evidence.\(index)",
                title: source.title,
                detail: source.description ?? source.url ?? "온톨로지 source 노드입니다.",
                symbolName: symbolName(forSourceURL: source.url ?? source.sourceURLs?.first)
            )
        }

        if !evidence.isEmpty {
            return evidence
        }

        return (node.sourceURLs ?? []).prefix(4).enumerated().map { index, urlString in
            DraftInfoItem(
                id: "\(node.id).evidence.url.\(index)",
                title: publisher(for: urlString),
                detail: urlString,
                symbolName: symbolName(forSourceURL: urlString)
            )
        }
    }

    private static func boundaryChecks(for node: DraftOntologyNode) -> [DraftInfoItem] {
        let checks = (node.criteria ?? []).prefix(5).enumerated().map { index, criterion in
            DraftInfoItem(
                id: "\(node.id).boundary.\(index)",
                title: criterion.label ?? criterion.basis ?? "경계선 확인",
                detail: criterion.selectionRule ?? criterion.condition ?? criterion.note ?? criterion.basisLookup ?? "구조화된 금액·비율·기간 필드를 함께 확인합니다.",
                symbolName: "checklist"
            )
        }

        if !checks.isEmpty {
            return checks
        }

        return [
            DraftInfoItem(
                id: "\(node.id).boundary.description",
                title: "공식 기준 확인",
                detail: node.description ?? "\(node.title) 적용 경계를 공식 출처로 확인합니다.",
                symbolName: "checklist"
            )
        ]
    }

    private static func checkLinks(
        for node: DraftOntologyNode,
        sourceNodes: [DraftOntologyNode]
    ) -> [DraftCheckLink] {
        var seenURLs = Set<String>()
        var links: [DraftCheckLink] = []

        for source in sourceNodes {
            let urlString = source.url ?? source.sourceURLs?.first
            guard let urlString, seenURLs.insert(urlString).inserted else { continue }
            links.append(
                DraftCheckLink(
                    id: "\(node.id).link.\(source.id)",
                    title: source.title,
                    detail: source.description ?? "온톨로지 source 노드입니다.",
                    publisher: publisher(for: urlString),
                    url: safeURL(urlString),
                    symbolName: symbolName(forSourceURL: urlString)
                )
            )
        }

        for (index, urlString) in (node.sourceURLs ?? []).enumerated() where seenURLs.insert(urlString).inserted {
            links.append(
                DraftCheckLink(
                    id: "\(node.id).link.url.\(index)",
                    title: publisher(for: urlString),
                    detail: "온톨로지 source_urls에 연결된 공식 자료입니다.",
                    publisher: publisher(for: urlString),
                    url: safeURL(urlString),
                    symbolName: symbolName(forSourceURL: urlString)
                )
            )
        }

        return links
    }

    private static func referencedSourceNodes(
        for node: DraftOntologyNode,
        nodesByID: [String: DraftOntologyNode]
    ) -> [DraftOntologyNode] {
        var sourceIDs: [String] = []
        sourceIDs.append(contentsOf: node.sources ?? [])
        sourceIDs.append(contentsOf: (node.criteria ?? []).compactMap(\.source))
        sourceIDs.append(contentsOf: (node.criteria ?? []).compactMap(\.basisSource))

        var seenIDs = Set<String>()
        return sourceIDs.compactMap { sourceID in
            guard seenIDs.insert(sourceID).inserted else { return nil }
            return nodesByID[sourceID]
        }
    }

    private static func localizedType(_ type: String) -> String {
        switch type {
        case "tax-credit":
            return "세액공제"
        case "deduction":
            return "소득공제"
        case "tax":
            return "세목"
        case "support-program":
            return "정책지원"
        case "eligibility-rule":
            return "요건 규칙"
        case "life-income":
            return "생활소득"
        case "filing":
            return "신고"
        case "concept":
            return "개념"
        default:
            return type
        }
    }

    private static func symbolName(for node: DraftOntologyNode) -> String {
        if let override = symbolOverrides[node.id] {
            return override
        }

        switch node.type {
        case "tax-credit":
            return "checkmark.seal"
        case "deduction":
            return "minus.circle"
        case "tax":
            return "sum"
        case "support-program":
            return "hands.sparkles"
        case "eligibility-rule":
            return "checklist"
        case "life-income":
            return "doc.text.magnifyingglass"
        case "filing":
            return "calendar"
        case "concept":
            return "lightbulb"
        default:
            return "doc.text"
        }
    }

    private static func symbolName(forBasis basis: String?) -> String {
        switch basis {
        case "earned-income", "income", "tax-base", "revenue":
            return "person.text.rectangle"
        case "asset":
            return "house.and.flag"
        case "age":
            return "person.crop.circle"
        case "median-income":
            return "person.3"
        case "limit", "official-standard":
            return "checklist"
        default:
            return "square.and.pencil"
        }
    }

    private static func symbolName(forSourceURL urlString: String?) -> String {
        guard let urlString else { return "link" }

        if urlString.contains("law.go.kr") {
            return "building.columns"
        }
        if urlString.contains("nts.go.kr") || urlString.contains("hometax.go.kr") {
            return "doc.text.magnifyingglass"
        }
        if urlString.contains("gov.kr") {
            return "person.crop.rectangle"
        }
        if urlString.contains("fsc.go.kr") || urlString.contains("kinfa") {
            return "wallet.pass"
        }
        return "link"
    }

    private static func tint(for id: String) -> Color {
        let palette = [
            Color(red: 0.51, green: 0.78, blue: 0.70),
            Color(red: 0.97, green: 0.73, blue: 0.61),
            Color(red: 0.53, green: 0.68, blue: 0.95),
            Color(red: 0.95, green: 0.76, blue: 0.46),
            Color(red: 0.66, green: 0.81, blue: 0.93),
            Color(red: 0.77, green: 0.70, blue: 0.95),
            Color(red: 0.75, green: 0.83, blue: 0.54),
            Color(red: 0.86, green: 0.75, blue: 0.95)
        ]
        let sum = id.unicodeScalars.reduce(0) { $0 + Int($1.value) }
        return palette[sum % palette.count]
    }

    private static func publisher(for urlString: String) -> String {
        if urlString.contains("law.go.kr") {
            return "법제처"
        }
        if urlString.contains("hometax.go.kr") {
            return "국세청 홈택스"
        }
        if urlString.contains("nts.go.kr") {
            return "국세청"
        }
        if urlString.contains("gov.kr") {
            return "정부24"
        }
        if urlString.contains("fsc.go.kr") {
            return "금융위원회"
        }
        if urlString.contains("kinfa") {
            return "서민금융진흥원"
        }
        if urlString.contains("korea.kr") {
            return "대한민국 정책브리핑"
        }

        return URL(string: urlString)?.host ?? "공식 출처"
    }

    private static func safeURL(_ urlString: String) -> URL {
        if let directURL = URL(string: urlString) {
            return directURL
        }

        if let encoded = urlString.addingPercentEncoding(withAllowedCharacters: .urlFragmentAllowed),
           let encodedURL = URL(string: encoded) {
            return encodedURL
        }

        return URL(string: "https://www.nts.go.kr")!
    }

    private static let symbolOverrides: [String: String] = [
        "credit.pension-account": "calendar.badge.clock",
        "credit.monthly-rent": "house",
        "deduction.housing-savings": "house.lodge",
        "tax.income.comprehensive": "sum",
        "concept.capital-gains.stock-basic-deduction": "chart.line.uptrend.xyaxis",
        "concept.simple-vat-taxpayer": "storefront",
        "support.earned-income-tax-credit": "hands.sparkles",
        "support.isa": "wallet.pass",
        "support.youth-leap-account": "sparkles",
        "eligibility-rule.credit-card-floor": "creditcard",
        "life-income.freelance-income": "doc.text.magnifyingglass"
    ]
}

private struct DraftCriterionBaseline {
    let suffix: String
    let title: String
    let label: String
    let value: Decimal
    let unit: String
}

private struct DraftOntologyExport: Decodable {
    let items: [DraftOntologyNode]
}

private struct DraftOntologyNode: Decodable {
    let id: String
    let title: String
    let type: String
    let description: String?
    let url: String?
    let sourceURLs: [String]?
    let sources: [String]?
    let parents: [String]?
    let children: [String]?
    let criteria: [DraftOntologyCriterion]?

    private enum CodingKeys: String, CodingKey {
        case id
        case title
        case type
        case description
        case url
        case sourceURLs = "source_urls"
        case sources
        case parents
        case children
        case criteria
    }
}

private struct DraftOntologyCriterion: Decodable {
    let label: String?
    let basis: String?
    let condition: String?
    let note: String?
    let benefit: String?
    let source: String?
    let basisSource: String?
    let basisCategory: String?
    let basisDefinition: String?
    let basisLookup: String?
    let selectionRule: String?
    let rateLabel: String?
    let amountFormula: String?
    let thresholdKrwMax: Decimal?
    let thresholdKrwMin: Decimal?
    let limitKrw: Decimal?
    let deductionKrw: Decimal?
    let maxAmountKrw: Decimal?
    let progressiveDeductionKrw: Decimal?
    let ratePercent: Decimal?
    let ratePercentMin: Decimal?
    let ratePercentMax: Decimal?
    let medianIncomePercentMax: Decimal?
    let ageMin: Decimal?
    let ageMax: Decimal?

    private enum CodingKeys: String, CodingKey {
        case label
        case basis
        case condition
        case note
        case benefit
        case source
        case basisSource = "basis_source"
        case basisCategory = "basis_category"
        case basisDefinition = "basis_definition"
        case basisLookup = "basis_lookup"
        case selectionRule = "selection_rule"
        case rateLabel = "rate_label"
        case amountFormula = "amount_formula"
        case thresholdKrwMax = "threshold_krw_max"
        case thresholdKrwMin = "threshold_krw_min"
        case limitKrw = "limit_krw"
        case deductionKrw = "deduction_krw"
        case maxAmountKrw = "max_amount_krw"
        case progressiveDeductionKrw = "progressive_deduction_krw"
        case ratePercent = "rate_percent"
        case ratePercentMin = "rate_percent_min"
        case ratePercentMax = "rate_percent_max"
        case medianIncomePercentMax = "median_income_percent_max"
        case ageMin = "age_min"
        case ageMax = "age_max"
    }
}

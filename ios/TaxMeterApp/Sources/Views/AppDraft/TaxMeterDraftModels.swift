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
    let symbolName: String
    let tint: Color
    let criteria: [DraftCriterion]
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

struct DraftAssetItem: Identifiable, Hashable {
    let id: String
    let title: String
    let symbolName: String
    let guidance: String
    let url: URL
    var amount: String
}

enum TaxMeterDraftData {
    static let categories: [DraftCategory] = [
        .init(id: "income", title: "소득"),
        .init(id: "deduction", title: "공제"),
        .init(id: "investment", title: "투자"),
        .init(id: "business", title: "사업"),
        .init(id: "policy", title: "정책")
    ]

    static let taxItems: [DraftTaxItem] = [
        .init(
            id: "financial-income",
            categoryID: "income",
            title: "금융소득",
            subtitle: "이자와 배당 합산",
            description: "이자소득과 배당소득 합계가 금융소득 종합과세 기준선에 얼마나 가까운지 확인합니다.",
            symbolName: "banknote",
            tint: Color(red: 0.43, green: 0.68, blue: 0.92),
            criteria: [
                .init(id: "financial-income-20m", title: "금융소득 종합과세", currentValue: 18_400_000, baselineValue: 20_000_000, unit: "원", note: "2,000만원 기준의 92% 수준입니다."),
                .init(id: "dividend-share", title: "배당소득 비중", currentValue: 8_200_000, baselineValue: 20_000_000, unit: "원", note: "배당금 자료와 원천징수 내역을 함께 확인합니다.")
            ]
        ),
        .init(
            id: "other-income",
            categoryID: "income",
            title: "기타소득",
            subtitle: "강연료, 원고료 등",
            description: "원천징수된 기타소득이 선택적 분리과세 기준에 들어오는지 확인합니다.",
            symbolName: "doc.text.magnifyingglass",
            tint: Color(red: 0.74, green: 0.69, blue: 0.94),
            criteria: [
                .init(id: "other-income-3m", title: "기타소득금액", currentValue: 3_250_000, baselineValue: 3_000_000, unit: "원", note: "기준선을 초과했습니다. 종합소득 합산 여부를 확인하세요.")
            ]
        ),
        .init(
            id: "pension-credit",
            categoryID: "deduction",
            title: "연금계좌",
            subtitle: "연금저축과 IRP",
            description: "연금저축과 퇴직연금 계좌 납입액이 세액공제 대상 한도에 접근했는지 봅니다.",
            symbolName: "calendar.badge.clock",
            tint: Color(red: 0.51, green: 0.78, blue: 0.70),
            criteria: [
                .init(id: "pension-saving-6m", title: "연금저축", currentValue: 5_700_000, baselineValue: 6_000_000, unit: "원", note: "한도에 근접했습니다."),
                .init(id: "pension-total-9m", title: "연금계좌 통합", currentValue: 8_200_000, baselineValue: 9_000_000, unit: "원", note: "통합 한도까지 여유가 남아 있습니다.")
            ]
        ),
        .init(
            id: "monthly-rent",
            categoryID: "deduction",
            title: "월세 세액공제",
            subtitle: "무주택, 전입, 임차 조건",
            description: "월세액과 총급여 기준을 함께 보고, 무주택 및 전입신고 조건은 체크리스트로 확인합니다.",
            symbolName: "house",
            tint: Color(red: 0.94, green: 0.70, blue: 0.58),
            criteria: [
                .init(id: "rent-salary-80m", title: "총급여 기준", currentValue: 72_000_000, baselineValue: 80_000_000, unit: "원", note: "총급여 기준에 근접했습니다."),
                .init(id: "rent-paid-10m", title: "연 월세액 한도", currentValue: 9_600_000, baselineValue: 10_000_000, unit: "원", note: "공제 대상 월세액 한도에 근접했습니다.")
            ]
        ),
        .init(
            id: "card-spend",
            categoryID: "deduction",
            title: "카드 사용액",
            subtitle: "총급여 25% 초과분",
            description: "신용카드, 체크카드, 현금영수증 사용액이 총급여 대비 공제 시작선에 도달했는지 확인합니다.",
            symbolName: "creditcard",
            tint: Color(red: 0.58, green: 0.75, blue: 0.95),
            criteria: [
                .init(id: "card-25-percent", title: "총급여 대비 사용률", currentValue: 0.28, baselineValue: 0.25, unit: "비율", note: "공제 시작선을 넘었습니다. 결제수단별 공제율을 확인하세요.")
            ]
        ),
        .init(
            id: "foreign-stock",
            categoryID: "investment",
            title: "해외주식",
            subtitle: "양도차익 기본공제",
            description: "해외주식 매도 손익이 연간 기본공제 기준을 넘었는지 확인합니다.",
            symbolName: "chart.xyaxis.line",
            tint: Color(red: 0.67, green: 0.79, blue: 0.56),
            criteria: [
                .init(id: "foreign-stock-2_5m", title: "양도차익", currentValue: 3_100_000, baselineValue: 2_500_000, unit: "원", note: "기준선을 초과했습니다. 매도 내역과 취득가를 확인하세요.")
            ]
        ),
        .init(
            id: "simple-vat",
            categoryID: "business",
            title: "간이과세",
            subtitle: "공급대가 기준",
            description: "개인사업자의 직전연도 공급대가가 간이과세 기준에 접근했는지 확인합니다.",
            symbolName: "briefcase",
            tint: Color(red: 0.91, green: 0.78, blue: 0.51),
            criteria: [
                .init(id: "simple-vat-104m", title: "직전연도 공급대가", currentValue: 96_000_000, baselineValue: 104_000_000, unit: "원", note: "간이과세 기준에 근접했습니다. 업종 예외를 확인하세요.")
            ]
        ),
        .init(
            id: "earned-income-credit",
            categoryID: "policy",
            title: "근로장려금",
            subtitle: "가구 유형별 소득선",
            description: "가구 유형별 총소득 기준선을 기준으로 장려금 검토가 필요한지 확인합니다.",
            symbolName: "giftcard",
            tint: Color(red: 0.90, green: 0.66, blue: 0.77),
            criteria: [
                .init(id: "eitc-dual-44m", title: "맞벌이 총소득", currentValue: 42_000_000, baselineValue: 44_000_000, unit: "원", note: "소득 기준선에 근접했습니다. 재산 요건을 함께 확인하세요.")
            ]
        )
    ]

    static let assetItems: [DraftAssetItem] = [
        .init(id: "deposit", title: "예금·현금", symbolName: "banknote", guidance: "은행 앱 또는 인터넷뱅킹의 전체계좌/잔액 조회 화면에서 확인합니다.", url: URL(string: "https://www.hometax.go.kr")!, amount: ""),
        .init(id: "stock", title: "국내·해외 주식", symbolName: "chart.xyaxis.line", guidance: "증권사 앱의 잔고, 실현손익, 해외주식 양도소득 자료를 내려받아 확인합니다.", url: URL(string: "https://www.nts.go.kr")!, amount: ""),
        .init(id: "pension", title: "연금계좌", symbolName: "calendar.badge.clock", guidance: "연금저축, IRP 납입액은 금융사 앱과 연말정산 간소화 자료에서 대조합니다.", url: URL(string: "https://www.hometax.go.kr")!, amount: ""),
        .init(id: "real-estate", title: "부동산", symbolName: "house", guidance: "실거래가, 공시가격, 등기부 정보를 함께 확인하고 보수적으로 입력합니다.", url: URL(string: "https://www.gov.kr")!, amount: ""),
        .init(id: "loan", title: "대출·채무", symbolName: "minus.circle", guidance: "은행/카드/신용정보 조회 서비스에서 잔액과 이자율을 확인합니다.", url: URL(string: "https://www.credit4u.or.kr")!, amount: "")
    ]
}

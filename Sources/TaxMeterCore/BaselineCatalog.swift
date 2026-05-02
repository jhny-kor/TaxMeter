import Foundation

public enum BaselineCatalog {
    public static let mvpTop15: [Baseline] = [
        .init(title: "금융소득 2,000만원", category: .financialIncome, threshold: 20_000_000, unit: "원"),
        .init(title: "피부양자 소득 2,000만원", category: .healthInsurance, threshold: 20_000_000, unit: "원"),
        .init(title: "연금저축 600만원", category: .deductions, threshold: 6_000_000, unit: "원"),
        .init(title: "연금계좌 통합 900만원", category: .deductions, threshold: 9_000_000, unit: "원"),
        .init(title: "기타소득 300만원", category: .comprehensiveIncome, threshold: 3_000_000, unit: "원"),
        .init(title: "간이과세자 1억400만원", category: .business, threshold: 104_000_000, unit: "원"),
        .init(title: "해외주식 250만원", category: .investment, threshold: 2_500_000, unit: "원"),
        .init(title: "신용카드 총급여 25%", category: .deductions, threshold: 0.25, unit: "비율"),
        .init(title: "청년도약계좌 총급여 7,500만원", category: .youthPolicy, threshold: 75_000_000, unit: "원"),
        .init(title: "근로장려금 맞벌이 4,400만원", category: .grant, threshold: 44_000_000, unit: "원"),
        .init(title: "월세 세액공제 총급여 8,000만원", category: .deductions, threshold: 80_000_000, unit: "원"),
        .init(title: "종합소득세 신고대상 소득", category: .comprehensiveIncome, threshold: 1, unit: "건"),
        .init(title: "ISA 가입 제한 확인", category: .investment, threshold: 1, unit: "여부"),
        .init(title: "국민연금 최소 수령 조건", category: .pension, threshold: 120, unit: "개월"),
        .init(title: "청약 가점 기본 계산", category: .subscription, threshold: 84, unit: "점")
    ]
}

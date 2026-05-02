import Testing
@testable import TaxMeterCore

struct BaselineEngineTests {
    @Test("MVP 기준선은 현행 검토값 15개를 유지")
    func mvpCatalogKeepsReviewedThresholds() {
        let catalog = BaselineCatalog.mvpTop15

        #expect(catalog.count == 15)
        #expect(catalog.contains { $0.title == "연금저축 600만원" && $0.threshold == 6_000_000 })
        #expect(catalog.contains { $0.title == "연금계좌 통합 900만원" && $0.threshold == 9_000_000 })
        #expect(catalog.contains { $0.title == "간이과세자 1억400만원" && $0.threshold == 104_000_000 })
    }

    @Test("거리 계산이 기준값-현재값으로 동작")
    func calculateDistance() {
        let baseline = Baseline(title: "금융소득 2,000만원", category: .financialIncome, threshold: 20_000_000, unit: "원")
        let engine = BaselineEngine()

        let result = engine.evaluate(baselines: [baseline], currentValues: [baseline.id: 18_000_000])

        #expect(result.count == 1)
        #expect(result[0].distance == 2_000_000)
        #expect(result[0].isExceeded == false)
    }

    @Test("초과 시 음수 거리")
    func exceededDistance() {
        let baseline = Baseline(title: "기타소득 300만원", category: .comprehensiveIncome, threshold: 3_000_000, unit: "원")
        let engine = BaselineEngine()

        let result = engine.evaluate(baselines: [baseline], currentValues: [baseline.id: 3_400_000])

        #expect(result[0].distance == -400_000)
        #expect(result[0].isExceeded)
    }
}

import Testing
@testable import TaxMeterCore

struct BaselineEngineTests {
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

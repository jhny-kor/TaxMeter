import SwiftUI

struct DashboardView: View {
    @ObservedObject var viewModel: DashboardViewModel

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Text("내 현재 위치 vs 제도 기준선 거리")
                        .font(.title3.bold())

                    ForEach(viewModel.distances, id: \.baseline.id) { distance in
                        BaselineCardView(
                            item: distance,
                            inputValue: viewModel.values[distance.baseline.id] ?? "",
                            onEdit: { viewModel.updateValue(for: distance.baseline.id, text: $0) }
                        )
                    }
                }
                .padding()
            }
            .navigationTitle("TaxMeter")
        }
    }
}

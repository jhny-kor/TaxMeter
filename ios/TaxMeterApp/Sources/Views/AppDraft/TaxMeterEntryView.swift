import SwiftUI

struct TaxMeterEntryView: View {
    @State private var showsSplash = true

    var body: some View {
        ZStack {
            TaxMeterHomeView()
                .opacity(showsSplash ? 0 : 1)

            if showsSplash {
                TaxMeterSplashView()
                    .transition(.opacity.combined(with: .scale(scale: 0.98)))
            }
        }
        .task {
            try? await Task.sleep(for: .milliseconds(850))
            withAnimation(.easeInOut(duration: 0.35)) {
                showsSplash = false
            }
        }
    }
}

private struct TaxMeterSplashView: View {
    var body: some View {
        ZStack {
            LinearGradient.taxMeterPastelBackground
                .ignoresSafeArea()

            VStack(spacing: 18) {
                TaxMeterAppIconView(size: 104)

                VStack(spacing: 6) {
                    Text("TaxMeter")
                        .font(.system(.largeTitle, design: .rounded, weight: .bold))
                        .foregroundStyle(Color.taxMeterInk)

                    Text("온톨로지 기준선과 확인 경로를 한 화면에서")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }
        }
    }
}

#Preview {
    TaxMeterEntryView()
}

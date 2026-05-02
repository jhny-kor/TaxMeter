# Repository Guidelines

## Project Structure & Module Organization

TaxMeter is split between a reusable Swift package and a SwiftUI iOS app.
Core tax-baseline logic lives in `Sources/TaxMeterCore`, with tests in
`Tests/TaxMeterCoreTests`. The iOS app lives in `ios/TaxMeterApp`; SwiftUI
views are under `ios/TaxMeterApp/Sources/Views`, app entry code is in
`ios/TaxMeterApp/Sources/App`, view models are in `Sources/ViewModels`, and
asset catalogs are in `Sources/Assets.xcassets`. Project notes and launch
planning live in `docs/`.

## Build, Test, and Development Commands

- `swift build`: builds the `TaxMeterCore` package.
- `swift test`: runs the Swift Testing suite for the core package.
- `swift test --disable-sandbox`: fallback when local Xcode/SwiftPM sandboxing
  blocks package tests.
- `cd ios/TaxMeterApp && xcodegen generate`: regenerates
  `TaxMeterApp.xcodeproj` from `project.yml` after project setting changes.
- `xcodebuild -project ios/TaxMeterApp/TaxMeterApp.xcodeproj -scheme TaxMeterApp -sdk iphonesimulator build`:
  builds the app for the simulator.

## Coding Style & Naming Conventions

Use Swift 5.10 and four-space indentation. Keep domain logic in
`TaxMeterCore` independent of SwiftUI so it stays testable. Name types with
`UpperCamelCase` (`BaselineEngine`, `DashboardViewModel`) and methods/properties
with `lowerCamelCase` (`evaluate`, `topRisks`). Prefer immutable `let` values,
small structs, and explicit access control for public package APIs. Keep Korean
tax labels and user-facing copy where they match the product domain.

## Testing Guidelines

Tests use Swift Testing (`import Testing`) and live under
`Tests/TaxMeterCoreTests`. Name test functions after the behavior being
protected, for example `calculateDistance()` or `exceededDistance()`. Add or
update tests when changing baseline thresholds, sorting rules, parsing, or
distance calculations. Run `swift test` before opening a pull request.

## Commit & Pull Request Guidelines

Recent history uses concise, imperative, intent-focused subjects, such as
`Make TaxMeter feel ready for app review`. For substantial changes, include a
short body with useful decision trailers such as `Constraint:`, `Rejected:`,
`Tested:`, and `Not-tested:`. Pull requests should summarize user-visible
changes, list verification commands, link related issues or docs, and include
screenshots for SwiftUI UI changes. Keep `project.yml` and the generated
`TaxMeterApp.xcodeproj` synchronized.

## Security & Configuration Tips

Do not commit personal tax data, credentials, provisioning profiles, or local
Xcode user settings. Keep baseline source notes in `docs/` when tax values are
updated so future changes can be reviewed against source assumptions.

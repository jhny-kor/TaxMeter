from __future__ import annotations

from support_deadline_parser import classify_deadline, parse_application_dates


def main() -> int:
    reference_date = "2026-07-11"
    cases = {
        "2025.6.11. 10:00 ~ 6.24. 18:00": ("2025-06-11", "2025-06-24"),
        "2025-06-11 ~ 2025-06-24": ("2025-06-11", "2025-06-24"),
        "6.11.(수) 10:00 ~ 6.24.(화) 18:00": ("2026-06-11", "2026-06-24"),
        "2025년 6월 11일부터 6월 24일까지": ("2025-06-11", "2025-06-24"),
        "2026.1.1. ~ 12.31.": ("2026-01-01", "2026-12-31"),
        "6.1. ~ 6.30.": ("2026-06-01", "2026-06-30"),
        "2026년 1월부터 12월까지": ("2026-01-01", "2026-12-31"),
    }
    for deadline, expected in cases.items():
        assert parse_application_dates(deadline, reference_date) == expected, deadline
    assert parse_application_dates("2026.01.13 ~ 2025.01.23.", reference_date) == (None, None)
    assert classify_deadline("상시") == "always_open"
    assert classify_deadline("연중 접수") == "always_open"
    assert classify_deadline("예산 소진 시까지") == "budget_exhaustion"
    assert classify_deadline("공고문 참조") == "announcement_based"
    assert classify_deadline("기관 문의") == "agency_contact_required"
    assert classify_deadline("신청기간 미정") == "schedule_pending"
    assert classify_deadline("매월 1일~10일") == "recurring_monthly"
    assert classify_deadline("분기별 접수") == "recurring_quarterly"
    assert classify_deadline("") == "date_missing"
    assert classify_deadline("날짜 원문 확인 불가") == "invalid_source_value"
    print(f"OK: {len(cases)} date ranges and 11 deadline states verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

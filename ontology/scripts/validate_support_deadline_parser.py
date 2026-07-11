from __future__ import annotations

from support_deadline_parser import classify_deadline, parse_application_dates


def main() -> int:
    reference_date = "2026-07-11"
    cases = {
        "2025.6.11. 10:00 ~ 6.24. 18:00": ("2025-06-11", "2025-06-24"),
        "2025-06-11 ~ 2025-06-24": ("2025-06-11", "2025-06-24"),
        "6.11.(수) 10:00 ~ 6.24.(화) 18:00": ("2026-06-11", "2026-06-24"),
        "2025년 6월 11일부터 6월 24일까지": ("2025-06-11", "2025-06-24"),
    }
    for deadline, expected in cases.items():
        assert parse_application_dates(deadline, reference_date) == expected, deadline
    assert parse_application_dates("2026.01.13 ~ 2025.01.23.", reference_date) == (None, None)
    assert classify_deadline("상시") == "always_open"
    assert classify_deadline("예산 소진 시까지") == "budget_exhaustion"
    assert classify_deadline("공고문 참조") == "announcement_based"
    assert classify_deadline("") == "date_missing"
    assert classify_deadline("접수 일정 확인 필요") == "date_parse_failed"
    print(f"OK: {len(cases)} date ranges and 5 deadline states verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from datetime import date
import re


APPLICATION_DATE_RE = re.compile(r"(?:(20\d{2})\s*(?:[.\-/년]\s*)?)?(\d{1,2})\s*[.\-/월]\s*(\d{1,2})")


def parse_application_dates(deadline_text: str, reference_date: str) -> tuple[str | None, str | None]:
    reference_year = date.fromisoformat(reference_date).year
    parsed_dates: list[date] = []
    latest_year = reference_year
    for match in APPLICATION_DATE_RE.finditer(deadline_text):
        year_text, month_text, day_text = match.groups()
        if year_text:
            latest_year = int(year_text)
        try:
            parsed_date = date(latest_year, int(month_text), int(day_text))
        except ValueError:
            continue
        if not year_text and parsed_dates and parsed_date < parsed_dates[-1]:
            parsed_date = date(latest_year + 1, int(month_text), int(day_text))
            latest_year += 1
        if parsed_dates and parsed_date < parsed_dates[-1]:
            return None, None
        parsed_dates.append(parsed_date)
    if not parsed_dates:
        return None, None
    return parsed_dates[0].isoformat(), parsed_dates[-1].isoformat()


def classify_deadline(deadline_text: str) -> str:
    compact_text = deadline_text.replace(" ", "")
    if "상시" in compact_text:
        return "always_open"
    if "예산소진" in compact_text:
        return "budget_exhaustion"
    if "공고문" in compact_text:
        return "announcement_based"
    return "date_parse_failed" if compact_text else "date_missing"

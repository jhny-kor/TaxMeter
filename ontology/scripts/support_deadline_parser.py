from __future__ import annotations

from calendar import monthrange
from datetime import date
import re


APPLICATION_DATE_RE = re.compile(r"(?:(20\d{2})\s*(?:[.\-/년]\s*)?)?(\d{1,2})\s*[.\-/월]\s*(\d{1,2})")
MONTH_RANGE_RE = re.compile(
    r"(?:(20\d{2})\s*년\s*)?(\d{1,2})\s*월\s*(?:부터|~|-|부터\s*)\s*(?:(20\d{2})\s*년\s*)?(\d{1,2})\s*월\s*(?:까지)?"
)

ALWAYS_OPEN_MARKERS = ("상시", "연중", "수시", "연중접수", "상시접수")
BUDGET_EXHAUSTION_MARKERS = ("예산소진", "예산소진시", "예산소진시까지", "자금소진", "소진시", "한도소진", "선착순")
ANNOUNCEMENT_MARKERS = ("별도공고", "공고문", "공고참조", "공고시", "추후공고", "홈페이지공고")
CONTACT_REQUIRED_MARKERS = ("기관문의", "문의", "담당자문의", "전화문의", "별도안내")
SCHEDULE_PENDING_MARKERS = ("미정", "확인필요", "일정확인", "접수일정", "추후안내")
RECURRING_MONTHLY_MARKERS = ("매월", "매달", "월별")
RECURRING_QUARTERLY_MARKERS = ("분기별", "분기마다", "분기")


def parse_application_dates(deadline_text: str, reference_date: str) -> tuple[str | None, str | None]:
    reference_year = date.fromisoformat(reference_date).year
    month_range = MONTH_RANGE_RE.search(deadline_text)
    if month_range:
        start_year_text, start_month_text, end_year_text, end_month_text = month_range.groups()
        start_year = int(start_year_text) if start_year_text else reference_year
        end_year = int(end_year_text) if end_year_text else start_year
        start_month = int(start_month_text)
        end_month = int(end_month_text)
        if end_year == start_year and end_month < start_month:
            end_year += 1
        try:
            start_date = date(start_year, start_month, 1)
            end_date = date(end_year, end_month, monthrange(end_year, end_month)[1])
        except ValueError:
            return None, None
        if end_date < start_date:
            return None, None
        return start_date.isoformat(), end_date.isoformat()

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
    if any(marker in compact_text for marker in ALWAYS_OPEN_MARKERS):
        return "always_open"
    if any(marker in compact_text for marker in BUDGET_EXHAUSTION_MARKERS):
        return "budget_exhaustion"
    if any(marker in compact_text for marker in ANNOUNCEMENT_MARKERS):
        return "announcement_based"
    if any(marker in compact_text for marker in CONTACT_REQUIRED_MARKERS):
        return "agency_contact_required"
    if any(marker in compact_text for marker in SCHEDULE_PENDING_MARKERS):
        return "schedule_pending"
    if any(marker in compact_text for marker in RECURRING_MONTHLY_MARKERS):
        return "recurring_monthly"
    if any(marker in compact_text for marker in RECURRING_QUARTERLY_MARKERS):
        return "recurring_quarterly"
    if not compact_text:
        return "date_missing"
    if "날짜 원문 확인 불가" in deadline_text:
        return "invalid_source_value"
    if any(token in compact_text for token in ("없음", "해당사항없음", "미정")):
        return "unsupported_date_format"
    return "unsupported_date_format"

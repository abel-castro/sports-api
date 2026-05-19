from datetime import UTC, date, datetime, timedelta


def get_date_30_days_ago() -> date:
    return (datetime.now(UTC) - timedelta(days=30)).date()

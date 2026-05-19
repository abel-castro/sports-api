from datetime import date

from freezegun import freeze_time

from sports_api.utils import get_date_30_days_ago


@freeze_time("2024-03-30")
def test_get_date_30_days_ago():
    expected_date = date(2024, 2, 29)
    assert get_date_30_days_ago() == expected_date

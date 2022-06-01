from datetime import datetime
from ..utils import get_shown_timedelta


def test_some():
    base = datetime(2020, 6, 15, 12, 30, 30)

    t = base.replace(year=2019)
    assert get_shown_timedelta(t, base) == "1年"

    t = base.replace(year=2019, month=2)
    assert get_shown_timedelta(t, base) == "1年4月"

    t = base.replace(year=2019, month=8)
    assert get_shown_timedelta(t, base) == "10月"

    t = base.replace(month=2)
    assert get_shown_timedelta(t, base) == "4月"

    t = base.replace(month=2, day=20)
    assert get_shown_timedelta(t, base) == "3月25天"

    t = base.replace(minute=25)
    assert get_shown_timedelta(t, base) == "5分钟"

    t = base.replace(minute=25, second=40)
    assert get_shown_timedelta(t, base) == "4分钟50秒"

    t = base.replace(second=25, microsecond=123)
    assert get_shown_timedelta(t, base) == "5秒"

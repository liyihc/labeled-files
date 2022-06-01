from datetime import datetime
from typing import Tuple


def func(v1: Tuple[int, int], v2: Tuple[int, int], split: int, s1: str, s2: str):
    if v1[0] < v2[0] - 1 or v1[0] == v2[0] - 1 and v1[1] <= v2[1]:
        a = v2[0] - v1[0]
        b = v2[1] - v1[1]
        if b < 0:
            b += split
            a -= 1
        elif not b:
            return f"{a}{s1}"
        return f"{a}{s1}{b}{s2}"


def get_shown_timedelta(dt: datetime, base: datetime | None = None):
    now = base or datetime.now()
    v1 = [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]
    v2 = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    split = [12, 30, 24, 60, 60]
    s = list("年月天")
    s.append("小时")
    s.append("分钟")
    s.append("秒")

    for i in range(len(s) - 1):
        ret = func((v1[i], v1[i + 1]), (v2[i], v2[i + 1]),
                   split[i], s[i], s[i + 1])
        if ret:
            return ret
        if v1[i] < v2[i]:
            v2[i + 1] += split[i]

    return f"{v2[-1]-v1[-1]}秒"

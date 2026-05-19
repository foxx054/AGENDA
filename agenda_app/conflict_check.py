from database import get_events_in_range
from utils import is_overlapping, parse_datetime


def check_conflict(start_date, end_date, exclude_id=None):
    events = get_events_in_range(start_date, end_date)
    conflicts = []
    for ev in events:
        if exclude_id and ev["id"] == exclude_id:
            continue
        e_start = parse_datetime(ev["start_date"])
        e_end = parse_datetime(ev["end_date"])
        if is_overlapping(
            parse_datetime(start_date), parse_datetime(end_date),
            e_start, e_end
        ):
            conflicts.append(ev)
    return conflicts

from datetime import datetime, timedelta

WEEKDAYS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
MONTHS = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
CATEGORIES = [
    {"id": "work", "label": "Trabalho", "color": "#4A90D9"},
    {"id": "personal", "label": "Pessoal", "color": "#10B981"},
    {"id": "health", "label": "Saúde", "color": "#EF4444"},
    {"id": "study", "label": "Estudo", "color": "#8B5CF6"},
    {"id": "finance", "label": "Finanças", "color": "#F59E0B"},
    {"id": "social", "label": "Social", "color": "#EC4899"},
    {"id": "other", "label": "Outro", "color": "#6B7280"},
]
REMINDER_OPTIONS = [
    ("No horário", 0),
    ("5 min antes", 5),
    ("10 min antes", 10),
    ("15 min antes", 15),
    ("30 min antes", 30),
    ("1 hora antes", 60),
    ("2 horas antes", 120),
    ("1 dia antes", 1440),
]


def format_date(date):
    return date.strftime("%d/%m/%Y")


def format_time(date):
    return date.strftime("%H:%M")


def format_datetime(date):
    return f"{format_date(date)} {format_time(date)}"


def parse_datetime(s):
    return datetime.fromisoformat(s)


def to_date_str(date):
    return date.strftime("%Y-%m-%d")


def get_week_days(date):
    start = date - timedelta(days=date.weekday())
    return [start + timedelta(days=i) for i in range(7)]


def get_month_days(year, month):
    import calendar
    cal = calendar.Calendar()
    return [d for d in cal.itermonthdates(year, month)]


def is_overlapping(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end

from datetime import datetime, timedelta

WEEKDAYS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
MONTHS = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
PRIORITIES = [
    {"id": 0, "label": "Baixa", "color": "#34C759", "light": "#E8F5E9", "icon": "↓"},
    {"id": 1, "label": "Média", "color": "#FF9500", "light": "#FFF3E0", "icon": "–"},
    {"id": 2, "label": "Alta", "color": "#FF3B30", "light": "#FFE5E5", "icon": "↑"},
]
LIGHT_GREEN = "#E8F5E9"
LIGHT_BLUE = "#E8F0FE"
LIGHT_RED = "#FFE5E5"
LIGHT_ORANGE = "#FFF3E0"

REPEAT_OPTIONS = [
    ("Não repetir", ""),
    ("Todo dia", "daily"),
    ("Toda semana", "weekly"),
    ("Todo mês", "monthly"),
    ("Personalizado", "custom"),
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


def format_time(time_str):
    if not time_str:
        return ""
    return time_str[:5]


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def to_date_str(date):
    return date.strftime("%Y-%m-%d")


def get_week_days(date):
    start = date - timedelta(days=date.weekday())
    return [start + timedelta(days=i) for i in range(7)]


def get_priority_info(priority_id):
    for p in PRIORITIES:
        if p["id"] == priority_id:
            return p
    return PRIORITIES[1]

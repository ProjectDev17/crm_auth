# =========================
# Construcción del item
# =========================
def now_ts() -> int:
    # Usa timestamp en segundos; equivalente a int(datetime.now().timestamp())
    return int(time.time())

#suma horas al timestamp actual
def add_hours_to_timestamp(hours: int) -> int:
    return int(time.time()) + hours * 3600
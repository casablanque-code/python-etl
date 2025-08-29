import re

# Алиасы заголовков (нормализуем: нижний регистр, схлопнутые пробелы)
COLUMN_ALIASES = {
    "inv": {
        "инвентарник","инв.номер","инв номер","инвентарный номер","инвкод","инв.код","инв. код","инв-номер","инв№",
        "inventory","inventory id","inventory code","inventory number",  # ← ВАЖНО: добавлено
        "equipment id","equipment_id","inv","asset id","asset","code","код"
    },
    "name": {
        "имя","наименование","оборудование","устройство","device","item","name","model","модель","title","описание","description"
    },
    "location": {
        "локация","местоположение","кабинет","расположение","место","место установки","location","office","room","site","area"
    },
    "serial": {
        "серийный номер","серийный №","серийник","сер номер","сер. номер","s/n","sn","serial","serial number","серийный","srn"
    },
    "mac": {
        "mac","mac-addr","mac address","mac-адрес","mac адрес","macадрес","macaddr","macaddress","mac addr"
    },
}

TARGET_HEADERS_RU = ["инвентарник","имя","локация","серийник","мак"]

# Вместо жесткого regex используем нормализацию + startswith
INV_START = "990000"

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())

def clean_text(s):
    return "" if s is None else str(s).strip()

def clean_serial(s):
    return "" if s is None else str(s).strip().upper()

def clean_mac(s):
    if s is None:
        return ""
    x = str(s).strip().lower().replace(".", "").replace("-", "").replace(" ", "")
    x = re.sub(r"[^0-9a-f]", "", x)
    if len(x) == 12:
        return ":".join(x[i:i+2] for i in range(0,12,2)).upper()
    return str(s).strip().upper()

def normalize_inv_for_filter(s):
    # Удаляем всё, кроме цифр (покрывает '990000-123456', '990000 123456', '990000123456.0')
    return re.sub(r"\D", "", str(s or ""))

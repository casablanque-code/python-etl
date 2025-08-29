import re

# Алиасы заголовков (нижний регистр, без лишних пробелов)
COLUMN_ALIASES = {
    "inv": {
        "инвентарник","инв.номер","инв номер","инвентарный номер","инвкод",
        "inventory","inventory id","inventory code","equipment id","equipment_id","inv","code","код"
    },
    "name": {
        "имя","наименование","оборудование","устройство","device","item","name","model","модель","title"
    },
    "location": {
        "локация","местоположение","кабинет","расположение","location","office","room","место"
    },
    "serial": {
        "серийный номер","серийник","serial","s/n","sn","серийный№","сер номер","серийный","serial number"
    },
    "mac": {
        "mac","mac-addr","mac address","mac-адрес","mac адрес","macадрес","macaddr","macaddress"
    },
}

TARGET_HEADERS_RU = ["инвентарник","имя","локация","серийник","мак"]
REQUIRED_FIELDS = ["инвентарник","имя"]

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())

def clean_text(s):
    return "" if s is None else str(s).strip()

def clean_serial(s):
    return "" if s is None else str(s).strip().upper()

def clean_mac(s):
    if s is None:
        return ""
    x = str(s).strip().lower()
    x = re.sub(r"[^0-9a-f]", "", x)
    if len(x) == 12:
        return ":".join(x[i:i+2] for i in range(0,12,2)).upper()
    return str(s).strip().upper()

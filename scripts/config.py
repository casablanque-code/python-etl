import re
# Алиасы заголовков (нормализованные в нижний регистр, пробелы схлопнуты)
COLUMN_ALIASES = {
    "inv": {
        "инвентарник","инв.номер","инв номер","инвентарный номер","инвкод","инв.код","инв. код","инв-номер","инв№",
        "inventory","inventory id","inventory code","equipment id","equipment_id","inv","asset id","asset","code","код"
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
INV_FILTER_REGEX = re.compile(r"^\s*990000\d+\s*$")

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())
def clean_text(s): 
    return "" if s is None else str(s).strip()
def clean_serial(s): 
    return "" if s is None else str(s).strip().upper()
def clean_mac(s):
    if s is None: return ""
    x = str(s).strip().lower().replace(".", "").replace("-", "").replace(" ", "")
    x = re.sub(r"[^0-9a-f]", "", x)
    if len(x) == 12:
        return ":".join(x[i:i+2] for i in range(0,12,2)).upper()
    return str(s).strip().upper()

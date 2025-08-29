import re
COLUMN_ALIASES = {
    "inv": {"инвентарник","инв.номер","инв номер","инвентарный номер","инвкод","inventory","inventory id","inventory code","equipment id","equipment_id","inv","code","код","asset id","asset"},
    "name": {"имя","наименование","оборудование","устройство","device","item","name","model","модель","title","описание","description"},
    "location": {"локация","местоположение","кабинет","расположение","место","место установки","location","office","room","site","area"},
    "serial": {"серийный номер","серийный №","серийник","сер номер","s/n","sn","serial","serial number","серийный","srn"},
    "mac": {"mac","mac-addr","mac address","mac-адрес","mac адрес","macадрес","macaddr","macaddress"}
}
TARGET_HEADERS_RU = ["инвентарник","имя","локация","серийник","мак"]
REQUIRED_FIELDS = ["инвентарник","имя"]
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())
def clean_text(s): return "" if s is None else str(s).strip()
def clean_serial(s): return "" if s is None else str(s).strip().upper()
def clean_mac(s):
    if s is None: return ""
    x = str(s).strip().lower().replace(".", "").replace("-", "").replace(" ", "")
    x = re.sub(r"[^0-9a-f]", "", x)
    if len(x) == 12:
        return ":".join(x[i:i+2] for i in range(0,12,2)).upper()
    return str(s).strip().upper()

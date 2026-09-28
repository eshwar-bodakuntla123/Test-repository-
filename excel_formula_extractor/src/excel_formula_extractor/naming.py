import re
import unicodedata


def sanitize_name(value: str) -> str:
    """
    Convert a business header into a stable identifier.

    Examples:
        "Emission Factor" -> "Emission_Factor"
        "CO2 (%)"         -> "CO2"
        "Scope-1 Value"   -> "Scope_1_Value"
    """
    value = unicodedata.normalize("NFKC", str(value)).strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^0-9A-Za-z_]", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")

    if not value:
        return "Unnamed"

    if value[0].isdigit():
        value = "_" + value

    return value

from enum import Enum


class BtwSoort(Enum):
    """Snelstart BTW types."""

    GEEN = "Geen"
    VERKOPEN_LAAG = "VerkopenLaag"
    VERKOPEN_HOOG = "VerkopenHoog"
    VERKOPEN_OVERIG = "VerkopenOverig"
    VERKOPEN_VERLEGD = "VerkopenVerlegd"
    INKOPEN_LAAG = "InkopenLaag"
    INKOPEN_HOOG = "InkopenHoog"
    INKOPEN_OVERIG = "InkopenOverig"

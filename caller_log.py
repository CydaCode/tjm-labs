"""Local JSON file acting as a temporary caller database.

The Pharmacy Identification API only knows about existing customers. When a
caller isn't found there, we collect their details during onboarding and
save them here, keyed by phone number, so a repeat call from the same
number is recognized without asking again. The file is created lazily by
`save()` the first time an unknown caller is onboarded - never eagerly, and
never for callers the API already recognizes.
"""

import json
from dataclasses import asdict
from pathlib import Path

from pharmacy_service import Pharmacy

LOG_PATH = Path(__file__).parent / "caller_log.json"


def _read_all() -> dict:
    if not LOG_PATH.exists():
        return {}
    try:
        return json.loads(LOG_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def find_by_phone(phone: str) -> Pharmacy | None:
    """Return the previously-saved caller for `phone`, or None if not logged."""
    record = _read_all().get(phone)
    if not record:
        return None

    prescriptions = record.get("prescriptions")
    return Pharmacy(
        name=record["name"],
        rx_volume=record["rx_volume"],
        city=record.get("city"),
        state=record.get("state"),
        address=record.get("address"),
        email=record.get("email"),
        phone=phone,
        prescriptions=[tuple(item) for item in prescriptions] if prescriptions else None,
    )


def save(pharmacy: Pharmacy) -> None:
    """Persist a caller's details, keyed by their phone number."""
    if not pharmacy.phone:
        return
    records = _read_all()
    record = asdict(pharmacy)
    record.pop("phone")
    records[pharmacy.phone] = record
    LOG_PATH.write_text(json.dumps(records, indent=2))

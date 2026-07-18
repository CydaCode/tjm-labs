"""Looks up pharmacies by phone number via the Pharmacy Identification API."""

from dataclasses import dataclass

import requests

from constants import PHARMACY_API_URL, REQUEST_TIMEOUT_SECONDS


@dataclass
class Pharmacy:
    """A pharmacy caller, either identified via the API or collected during onboarding."""

    name: str
    rx_volume: int
    city: str | None = None
    state: str | None = None
    address: str | None = None
    email: str | None = None
    phone: str | None = None
    prescriptions: list[tuple[str, int]] | None = None

    @property
    def location(self) -> str:
        """Human-readable location. The API represents this as either city/state or
        a single address field depending on the record, so fall back accordingly."""
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        return self.city or self.state or self.address or "your area"


def _extract_rx_volume(record: dict) -> int:
    """Normalize the API's inconsistent Rx volume fields into a single integer."""
    if isinstance(record.get("rxVolume"), (int, float)):
        return int(record["rxVolume"])
    prescriptions = record.get("prescriptions") or []
    return sum(item.get("count", 0) for item in prescriptions)


def _extract_prescriptions(record: dict) -> list[tuple[str, int]] | None:
    prescriptions = record.get("prescriptions")
    if not prescriptions:
        return None
    return [(item.get("drug", "Unknown"), item.get("count", 0)) for item in prescriptions]


def _record_to_pharmacy(record: dict) -> Pharmacy:
    return Pharmacy(
        name=record.get("name", "Unknown Pharmacy"),
        rx_volume=_extract_rx_volume(record),
        city=record.get("city"),
        state=record.get("state"),
        address=record.get("address"),
        email=record.get("email"),
        phone=record.get("phone"),
        prescriptions=_extract_prescriptions(record),
    )


class PharmacyService:
    """Retrieves pharmacy records from the Pharmacy Identification API."""

    def __init__(self, base_url: str = PHARMACY_API_URL) -> None:
        self._base_url = base_url

    def find_by_phone(self, phone: str) -> Pharmacy | None:
        """Return the pharmacy matching `phone`, or None if not found or unreachable."""
        try:
            response = requests.get(self._base_url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
        except requests.RequestException:
            return None

        for record in response.json():
            if record.get("phone") == phone:
                return _record_to_pharmacy(record)
        return None

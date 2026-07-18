"""Mocked follow-up services: email notifications and callback scheduling."""

from utils import type_out
from constants import COLOR_SYSTEM


def send_followup_email(pharmacy_email: str | None) -> None:
    """Simulate queuing a follow-up email."""
    type_out("Sending follow-up email...", color=COLOR_SYSTEM)
    destination = pharmacy_email or "the email address on file"
    type_out(f"✓ Email queued successfully for {destination}.", color=COLOR_SYSTEM)


def schedule_callback(preferred_time: str) -> None:
    """Simulate scheduling a callback."""
    type_out("Callback scheduled.", color=COLOR_SYSTEM)
    type_out(f"Preferred time: {preferred_time}", color=COLOR_SYSTEM)

"""Generates response text for greetings and each supported intent. No I/O or side effects."""

from constants import RX_VOLUME_TIERS
from pharmacy_service import Pharmacy


def _rx_tier(rx_volume: int) -> str:
    for threshold, tier in RX_VOLUME_TIERS:
        if rx_volume >= threshold:
            return tier
    return "starter"


def known_caller_greeting(pharmacy: Pharmacy) -> str:
    """Greeting for a pharmacy recognized via the Pharmacy Identification API."""
    return (
        f"Hi, thanks for calling TJM Labs! I see you're calling from {pharmacy.name} "
        f"in {pharmacy.location}. Looks like you're processing around "
        f"{pharmacy.rx_volume} prescriptions a month with us on file. "
        "How can I help you today?"
    )


def unknown_caller_greeting() -> str:
    """Greeting for a caller not found in the Pharmacy Identification API."""
    return (
        "Hi, thanks for calling TJM Labs! I don't have your pharmacy on file yet, "
        "so I'd like to grab a couple of details before we continue."
    )


def returning_caller_greeting(pharmacy: Pharmacy) -> str:
    """Greeting for a caller not in the API, but recognized from a previous call."""
    return (
        f"Welcome back, {pharmacy.name}! I have you on file from a previous call,  "
        f"processing around {pharmacy.rx_volume} prescriptions a month. "
        "How can I help you today?"
    )


def missing_email_prompt() -> str:
    """Prompt used when an email is needed (to send or to answer) but none is on file."""
    return "I don't have an email on file for you yet. What's the best email to reach you at?"


def missing_location_prompt() -> str:
    """Prompt used when a caller asks about their location but none is on file."""
    return "I don't have a location on file for you yet. What city and state are you calling from?"


def pricing_response(pharmacy: Pharmacy) -> str:
    tier = _rx_tier(pharmacy.rx_volume)
    return (
        f"Based on your monthly volume of about {pharmacy.rx_volume} prescriptions, "
        f"you'd fall into our {tier} pricing tier. I can have someone send over exact "
        "numbers, or set up a callback with a sales rep - which would you prefer?"
    )


def demo_response() -> str:
    return (
        "I'd be happy to help set up a demo of TJM Labs' platform. "
        "I can schedule a callback with our sales team, or have a demo link sent to your email."
    )


def product_info_response() -> str:
    return (
        "TJM Labs provides tools that help pharmacies streamline prescription "
        "management and grow their business. If you'd like, I can have a specialist "
        "follow up with details specific to your pharmacy."
    )


def greeting_response() -> str:
    return "Hello! How can I help you today?"


def thanks_response() -> str:
    return "You're welcome! Is there anything else I can help you with?"


def closing_response() -> str:
    return "No problem. thanks for calling TJM Labs. Have a great day!"


def talk_to_human_response() -> str:
    return "I can have someone from our team call you directly. Would you like me to schedule that callback?"


def _full_account_summary(pharmacy: Pharmacy) -> str:
    lines = [
        f"Here's what I have on file for {pharmacy.name}:",
        f"- Location: {pharmacy.location}",
        f"- Monthly Rx volume: {pharmacy.rx_volume}",
        f"- Email: {pharmacy.email or 'not on file'}",
    ]
    if pharmacy.prescriptions:
        breakdown = ", ".join(f"{drug} ({count})" for drug, count in pharmacy.prescriptions)
        lines.append(f"- Prescriptions on file: {breakdown}")
    return "\n".join(lines)


def requested_account_fields(message: str) -> dict[str, bool]:
    """Which account fields a caller's message is asking about."""
    lowered = message.lower()
    wants_volume = "volume" in lowered
    wants_breakdown = any(k in lowered for k in ("prescription", "drug", "medication"))
    return {
        "email": "email" in lowered,
        "location": any(k in lowered for k in ("location", "address", "city", "state")),
        "volume": wants_volume,
        "breakdown": wants_breakdown,
        # A bare "rx" is ambiguous, so treat it like a breakdown request
        # unless "volume" is also present.
        "bare_rx": "rx" in lowered and not wants_volume and not wants_breakdown,
    }


def account_info_response(pharmacy: Pharmacy, message: str) -> str:
    """Answer only the specific field(s) a caller asked about, not the full record."""
    fields = requested_account_fields(message)
    if not any(fields.values()):
        return _full_account_summary(pharmacy)

    answers = []
    if fields["email"]:
        answers.append(f"Your email on file is {pharmacy.email or 'not on file'}.")
    if fields["location"]:
        answers.append(f"Your location on file is {pharmacy.location}.")
    if fields["volume"]:
        answers.append(f"Your monthly Rx volume on file is {pharmacy.rx_volume}.")
    if fields["breakdown"] or fields["bare_rx"]:
        if pharmacy.prescriptions:
            breakdown = ", ".join(f"{drug} ({count})" for drug, count in pharmacy.prescriptions)
            answers.append(f"Your prescriptions on file: {breakdown}.")
        elif not fields["volume"]:
            answers.append(f"Your monthly Rx volume on file is {pharmacy.rx_volume}.")
    return " ".join(answers)


def unsupported_response() -> str:
    """Safe fallback for requests outside the agent's supported domain."""
    return (
        "I'd love to help, but I want to make sure you get the right information. "
        "I can have a member of our team follow up by email or schedule a callback. "
        "Which would you prefer?"
    )


def exit_response() -> str:
    return "Thanks for calling TJM Labs. Have a great day!"

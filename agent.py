"""Top-level orchestration: identify the caller, onboard if needed, run the conversation."""

import re

import caller_log
from constants import (
    CALLBACK_TIME_ALIASES,
    CALLBACK_TIME_FILLER_PREFIXES,
    CALLBACK_TIME_OPTIONS,
    COLOR_AGENT,
    MOCK_CALLER_PHONE,
)
from conversation import ConversationEngine
from pharmacy_service import Pharmacy, PharmacyService
import responder
import tools
from utils import ask_caller, read_caller_message, say


def _normalize_callback_time(raw: str) -> str:
    """Turn a free-text time reply into a clean label, stripping conversational
    filler (e.g. "How about today?" -> "Today") and matching known phrasing."""
    cleaned = raw.strip().rstrip("?.! ")
    lowered = cleaned.lower()
    for prefix in CALLBACK_TIME_FILLER_PREFIXES:
        if lowered.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            lowered = cleaned.lower()
            break

    preset = next((option for option in CALLBACK_TIME_OPTIONS if lowered in option.lower()), None)
    alias = CALLBACK_TIME_ALIASES.get(lowered)
    return preset or alias or cleaned.title() or CALLBACK_TIME_OPTIONS[0]


class InboundSalesAgent:
    """Simulates one inbound call from identification through follow-up."""

    def __init__(self) -> None:
        self._pharmacy_service = PharmacyService()
        # Only callers the API doesn't know about are onboarded into the local
        # log, so only their details should ever be written back to it.
        self._is_logged_caller = False

    def run(self) -> None:
        """Run the full simulated call: identify, greet, converse, follow up."""
        pharmacy = self._identify_caller()
        engine = ConversationEngine(pharmacy)

        while True:
            user_message = read_caller_message()
            if not user_message:
                continue

            turn = engine.handle(user_message)
            say("Agent", turn.response, color=COLOR_AGENT)

            if turn.action == "email":
                self._handle_email(pharmacy)
            elif turn.action == "callback":
                self._handle_callback()
            elif turn.action == "collect_email":
                self._collect_field(pharmacy, "email")
            elif turn.action == "collect_location":
                self._collect_field(pharmacy, "address")

            if turn.should_exit:
                break

    def _identify_caller(self) -> Pharmacy:
        """Identify the caller via the API, then the local log, then onboard them."""
        pharmacy = self._pharmacy_service.find_by_phone(MOCK_CALLER_PHONE)
        if pharmacy:
            say("Agent", responder.known_caller_greeting(pharmacy), color=COLOR_AGENT)
            return pharmacy

        pharmacy = caller_log.find_by_phone(MOCK_CALLER_PHONE)
        if pharmacy:
            self._is_logged_caller = True
            say("Agent", responder.returning_caller_greeting(pharmacy), color=COLOR_AGENT)
            return pharmacy

        say("Agent", responder.unknown_caller_greeting(), color=COLOR_AGENT)
        name = ask_caller("What's your pharmacy's name?")
        rx_volume = self._prompt_for_rx_volume()
        pharmacy = Pharmacy(name=name or "your pharmacy", rx_volume=rx_volume, phone=MOCK_CALLER_PHONE)
        self._is_logged_caller = True
        caller_log.save(pharmacy)
        say("Agent", f"Thanks, {name}! Got it. How can I help you today?", color=COLOR_AGENT)
        return pharmacy

    def _handle_email(self, pharmacy: Pharmacy) -> None:
        if not pharmacy.email:
            pharmacy.email = ask_caller(responder.missing_email_prompt())
            if self._is_logged_caller:
                caller_log.save(pharmacy)
        tools.send_followup_email(pharmacy.email)

    def _collect_field(self, pharmacy: Pharmacy, field: str) -> None:
        """Save a value the caller provides in response to a 'missing field' prompt.

        The prompt itself was already printed as the agent's turn response, so
        this just reads the reply - no need to ask again.
        """
        setattr(pharmacy, field, read_caller_message())
        if self._is_logged_caller:
            caller_log.save(pharmacy)
        say("Agent", "Got it, thanks. I've saved that.", color=COLOR_AGENT)

    @staticmethod
    def _prompt_for_rx_volume() -> int:
        """Ask for the monthly Rx volume, pulling the number out of free text
        (e.g. "Panadol 30" -> 30) and re-asking once if none is found."""
        question = "About how many prescriptions do you fill per month?"
        for _ in range(2):
            raw = ask_caller(question)
            match = re.search(r"\d+", raw)
            if match:
                return int(match.group())
            question = "Sorry, I didn't catch a number, about how many prescriptions do you fill per month?"
        return 0

    @staticmethod
    def _handle_callback() -> None:
        options = ", ".join(CALLBACK_TIME_OPTIONS)
        raw = ask_caller(f"What time works best? ({options}, or another time that works for you)")
        tools.schedule_callback(_normalize_callback_time(raw))

"""Intent detection and the turn-by-turn conversation loop."""

from dataclasses import dataclass

from constants import (
    ACCOUNT_FIELD_WORDS,
    ACCOUNT_SELF_REFERENCE_WORDS,
    AFFIRMATIVE_KEYWORDS,
    INTENT_KEYWORDS,
    NEGATIVE_KEYWORDS,
)
from pharmacy_service import Pharmacy
import responder

# Intents whose responses end with an open-ended offer to follow up
# (email or callback), so a plain "yes"/"no" afterwards needs handling.
_INTENTS_WITH_OPEN_OFFER = {"unknown", "pricing", "demo", "product_info"}


def _is_account_info_query(lowered: str) -> bool:
    """True for phrasing like 'how many prescriptions do I have' or 'my rx volume' -
    a self-reference word plus a field word, anywhere in the message."""
    has_self_reference = any(word in lowered for word in ACCOUNT_SELF_REFERENCE_WORDS)
    has_field_word = any(word in lowered for word in ACCOUNT_FIELD_WORDS)
    return has_self_reference and has_field_word


def detect_intent(message: str) -> str:
    """Classify a user message into a supported intent using keyword matching."""
    lowered = message.lower()
    if any(keyword in lowered for keyword in INTENT_KEYWORDS["exit"]):
        return "exit"
    if any(keyword in lowered for keyword in INTENT_KEYWORDS["account_info"]):
        return "account_info"
    if _is_account_info_query(lowered):
        return "account_info"
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent in ("exit", "account_info"):
            continue
        if any(keyword in lowered for keyword in keywords):
            return intent
    return "unknown"


def _matches_short_reply(message: str, keywords: list[str]) -> bool:
    lowered = message.lower().strip().rstrip(".!")
    return any(lowered == kw or lowered.startswith(f"{kw} ") for kw in keywords)


def is_affirmative(message: str) -> bool:
    """Check whether a message is a plain 'yes' with no other content."""
    return _matches_short_reply(message, AFFIRMATIVE_KEYWORDS)


def is_negative(message: str) -> bool:
    """Check whether a message is a plain 'no' with no other content."""
    return _matches_short_reply(message, NEGATIVE_KEYWORDS)


@dataclass
class Turn:
    """The agent's reply to one user message, plus any follow-up action to take."""

    response: str
    action: str | None = None  # "email", "callback", "collect_email", "collect_location", or None
    should_exit: bool = False


def _account_info_turn(pharmacy: Pharmacy, user_message: str) -> Turn:
    """Answer an account_info query, or ask the caller to provide the field if missing."""
    fields = responder.requested_account_fields(user_message)
    if fields["email"] and not pharmacy.email:
        return Turn(response=responder.missing_email_prompt(), action="collect_email")
    if fields["location"] and not (pharmacy.city or pharmacy.state or pharmacy.address):
        return Turn(response=responder.missing_location_prompt(), action="collect_location")
    return Turn(response=responder.account_info_response(pharmacy, user_message))


_SIMPLE_RESPONSES = {
    "demo": responder.demo_response,
    "product_info": responder.product_info_response,
    "greeting": responder.greeting_response,
}


class ConversationEngine:
    """Drives the conversation for one caller, turn by turn."""

    def __init__(self, pharmacy: Pharmacy) -> None:
        self.pharmacy = pharmacy
        self.history: list[tuple[str, str]] = []
        self._awaiting_followup_choice = False
        self._awaiting_anything_else = False
        self._awaiting_callback_confirmation = False

    def handle(self, user_message: str) -> Turn:
        """Process one user message and return the agent's reply."""
        self.history.append(("caller", user_message))

        if self._awaiting_callback_confirmation:
            self._awaiting_callback_confirmation = False
            if is_affirmative(user_message):
                turn = Turn(response="Sure, I can set that up.", action="callback")
                self.history.append(("agent", turn.response))
                return turn
            if is_negative(user_message):
                turn = self._close(responder.closing_response())
                self.history.append(("agent", turn.response))
                return turn
            # Anything else: drop the offer and handle this message normally.

        if self._awaiting_followup_choice and is_negative(user_message):
            turn = self._close(responder.closing_response())
            self.history.append(("agent", turn.response))
            return turn

        if self._awaiting_followup_choice and is_affirmative(user_message):
            turn = Turn(response="Would you like me to schedule a callback, or send a follow-up email?")
            self._awaiting_followup_choice = False
            self.history.append(("agent", turn.response))
            return turn

        if self._awaiting_anything_else:
            self._awaiting_anything_else = False
            if is_negative(user_message):
                turn = self._close(responder.closing_response())
                self.history.append(("agent", turn.response))
                return turn
            if is_affirmative(user_message):
                turn = Turn(response="Sure, what can I help you with?")
                self.history.append(("agent", turn.response))
                return turn

        intent = detect_intent(user_message)

        if intent == "exit":
            turn = self._close(responder.exit_response())
        elif intent == "account_info":
            turn = _account_info_turn(self.pharmacy, user_message)
        elif intent == "pricing":
            turn = Turn(response=responder.pricing_response(self.pharmacy))
        elif intent == "callback":
            turn = Turn(response="Sure, I can set that up.", action="callback")
        elif intent == "talk_to_human":
            turn = Turn(response=responder.talk_to_human_response())
        elif intent == "email":
            turn = Turn(response="Sure, I can send that over.", action="email")
        elif intent == "thanks":
            turn = Turn(response=responder.thanks_response())
            self._awaiting_anything_else = True
        elif intent in _SIMPLE_RESPONSES:
            turn = Turn(response=_SIMPLE_RESPONSES[intent]())
        else:
            turn = Turn(response=responder.unsupported_response())

        self._awaiting_followup_choice = intent in _INTENTS_WITH_OPEN_OFFER
        self._awaiting_callback_confirmation = intent == "talk_to_human"
        self.history.append(("agent", turn.response))
        return turn

    @staticmethod
    def _close(message: str) -> Turn:
        return Turn(response=message, should_exit=True)

"""Static configuration: API endpoint, mock caller data, intent keywords, and display settings."""

PHARMACY_API_URL = "https://67e14fb758cc6bf785254550.mockapi.io/pharmacies" #This api is supposed to be in the .env file, but for now it is hardcoded here for testing purposes.

# Simulated inbound caller. Change to a number not present in the API

#MOCK_CALLER_PHONE = "+1-555-000-0000" # unrecognized caller
MOCK_CALLER_PHONE = "+1-555-123-4567" # recognized caller

REQUEST_TIMEOUT_SECONDS = 5

APP_HEADER = (
    "\n"
    "\n"
    "=========================================\n"
    " TJM Labs - Inbound Pharmacy Sales Agent\n"
    "========================================="
    "\n"
)

# Checked in order; the first intent whose keywords appear in the message wins.
INTENT_KEYWORDS = {
    "exit": [
        "exit", "quit", "bye", "goodbye", "hang up", "that's all", "nothing else", "nothing",
        "end the call", "end this call", "end call",
    ],
   
    "account_info": [
        "my profile", "my account", "my information", "my details", "my record",
        "my pharmacy name", "check my record", "what's my", "what is my",
        "tell me my", "do you have my", "on file for me",
    ],
    "pricing": ["price", "pricing", "cost", "how much", "rates", "quote"],
    "demo": ["demo", "demonstration", "trial", "show me", "walkthrough"],
    "callback": [
        "call me", "callback", "call back", "phone me", "ring me", "call for me",
        "schedule a call", "schedule a callback", "set up a call", "set up a callback",
        "book a call", "book a callback", "arrange a call",
    ],
    # Wanting to speak with a live person - offer a callback rather than
    # falling through to the generic unsupported response.
    "talk_to_human": [
        "talk to someone", "speak to someone", "talk to somebody", "speak with someone",
        "talk to a person", "speak to a person", "talk to a rep", "speak to a rep",
        "talk to a human", "speak to a human", "who can i talk to", "who do i talk to",
        "can i talk to", "can i speak to", "talk to anybody", "speak to anybody",
        "call anybody", "talk to anyone", "speak to anyone", "speak with anyone",
        "anyone from your team", "anybody from your team", "call someone",
    ],
    "email": [
        "email", "send me an email", "send an email", "mail me the",
        "follow up by email", "follow up over email",
    ],
    "product_info": [
        "product", "tell me about", "tell me more", "more about", "what you do",
        "what do you do", "what do you offer", "service", "services",
        "offer", "about tjm", "who are you", "how can you help", "help my pharmacy",
        "what can you do for",
    ],
    "thanks": ["thank you", "thanks", "thank u", "appreciate it", "appreciated"],
    "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
}

# General "account_info" match: a self-reference word ("my", "how many", ...)
# together with a field word ("email", "prescription", ...) anywhere in the
# message, e.g. "how many prescriptions do I have", "what's my rx volume".
ACCOUNT_SELF_REFERENCE_WORDS = ["my", "how many", "do i have", "i have", "on file", "what about"]
ACCOUNT_FIELD_WORDS = [
    "email", "prescription", "rx", "volume", "location", "address", "city", "state",
    "record", "profile", "account", "details", "information",
]

# Phrases treated as "yes" when replying to an open-ended follow-up offer.
AFFIRMATIVE_KEYWORDS = [
    "yes", "yeah", "yep", "sure", "please do", "sounds good", "go ahead", "okay", "ok",
]

# Phrases treated as "no" when replying to an open-ended follow-up offer,
# or when asked if the caller needs anything else.
NEGATIVE_KEYWORDS = [
    "no", "nope", "no thanks", "not now", "nothing else", "that's all",
    "i'm good", "im good", "all good", "we're good", "Nothing",
]

RX_VOLUME_TIERS = (
    (5000, "enterprise"),
    (1000, "growth"),
    (0, "starter"),
)

CALLBACK_TIME_OPTIONS = ["Tomorrow Morning", "Tomorrow Afternoon", "This Evening"]

# Common phrasing for times outside the presets, normalized to a clean label.
CALLBACK_TIME_ALIASES = {
    "today": "Today",
    "this morning": "This Morning",
    "this afternoon": "This Afternoon",
    "this evening": "This Evening",
    "tonight": "This Evening",
    "tomorrow": "Tomorrow Morning",
    "now": "As Soon As Possible",
    "asap": "As Soon As Possible",
    "as soon as possible": "As Soon As Possible",
}

# Conversational filler stripped off the front of a free-text time reply,
# e.g. "How about today?" -> "today".
CALLBACK_TIME_FILLER_PREFIXES = [
    "how about ", "what about ", "can we do ", "can you do ", "could we do ",
    "let's do ", "lets do ", "maybe ", "i'd prefer ", "i would prefer ",
]

TYPING_DELAY_SECONDS = 0.02

COLOR_AGENT = "\033[36m"   # cyan
COLOR_USER = "\033[33m"    # yellow
COLOR_SYSTEM = "\033[90m"  # grey
COLOR_RESET = "\033[0m"

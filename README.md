# TJM Labs - Inbound Pharmacy Sales Agent

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The simulated caller's phone number is set in `constants.py` via `MOCK_CALLER_PHONE`. Swap between the two lines to try either path:

```python
MOCK_CALLER_PHONE = "+1-555-123-4567"  # known caller - found via the Pharmacy Identification API
MOCK_CALLER_PHONE = "+1-555-000-0000"  # unknown caller - triggers onboarding (name + Rx volume)
```

Type naturally at the `You:` prompt (e.g. `I want pricing`, `can I schedule a demo?`, `exit`). No menus, no numbered options.

## What this is

A terminal simulation of an AI-powered inbound sales agent for TJM Labs. A pharmacy calls in, the agent identifies them by phone number, and a rule-based conversation engine handles pricing, demo, product, and account questions - routing anything outside its depth to a callback or follow-up email.

This is a take-home style implementation: it favors a small, readable, well-separated codebase over production features. No web framework, no LLM/AI SDK - just deterministic keyword matching, as specified in the brief.

## How a call flows

1. **Identify the caller** by phone number, checked in this order:
   - **Pharmacy Identification API** (source of truth for existing customers)
   - **Local caller log** (`caller_log.json`) - callers the API doesn't know about, onboarded on a previous call
   - **Onboarding** - if neither has them, ask for pharmacy name and monthly Rx volume, then save to the local log
2. **Converse** - keyword-based intent detection handles pricing, demos, product questions, account-info lookups, callback/email requests, thanks, and small talk. Anything unsupported gets a safe fallback that offers a callback or email instead of guessing.
3. **Follow up** - a callback gets "scheduled" (mocked) with a caller-supplied time; a follow-up email gets "queued" (mocked), asking for an email address first if none is on file.

### The caller log

The Pharmacy Identification API only knows about existing customers. `caller_log.py` is a small local JSON file acting as a temporary database for everyone else: it's created the first time an unknown number is onboarded, and updated as that caller provides more details (email, location) across the conversation. Calling back from the same number later skips onboarding and picks up where things left off.

It's deliberately never written to for callers the API *does* recognize - the API stays the single source of truth for real customers; the log only fills the gap for people it doesn't cover.

## Project layout

| File | Responsibility |
|---|---|
| `main.py` | Entry point - clears the screen, prints the header, starts the call |
| `agent.py` | Orchestration - identify caller, run the conversation loop, execute follow-up actions |
| `conversation.py` | Turn-by-turn state machine - intent detection, "yes/no" follow-up handling |
| `responder.py` | Pure response text for every intent - no I/O |
| `pharmacy_service.py` | Talks to the Pharmacy Identification API, normalizes its inconsistent record shapes |
| `caller_log.py` | Local JSON store for callers the API doesn't know about |
| `tools.py` | Mocked email and callback follow-up actions |
| `constants.py` | Config, intent keywords, colors, timing |
| `utils.py` | Terminal helpers - screen clearing, colorized/typed output, prompts |

## Assumptions and tradeoffs

- Intent detection is deterministic keyword matching, not an LLM - predictable and easy to test, at the cost of natural-language flexibility. Swapping in an LLM later would only mean replacing `conversation.py`'s intent detection; the rest of the flow (identify -> converse -> follow up) stays the same.
- Email and callback are mocked - they print a confirmation instead of calling a real service.
- The Pharmacy Identification API is treated as the source of truth; the local caller log only covers what the API doesn't.


-------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
## If I had 3 more hours, what would I do?
-------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------

With an additional three hours, I would focus on improving the realism, robustness, and extensibility of the solution rather than adding unrelated features.

First, I would replace the rule-based intent detection with an LLM-powered conversation engine. This would enable the agent to better understand natural language, handle a wider variety of user requests, maintain richer conversational context, and generate more natural responses while continuing to use the same pharmacy lookup and follow-up workflows.

Second, I would replace the mocked email and callback services with real integrations, allowing the agent to send actual follow-up emails and create calendar events or CRM tasks.

Third, I would improve reliability by adding automated unit tests, stronger input validation, structured logging, and more comprehensive error handling for API failures and unexpected user input.

Finally, I would enhance the user experience by improving the terminal interface with richer formatting, conversation history, and clearer status updates, making the application feel closer to a production-ready support tool while preserving its simplicity.
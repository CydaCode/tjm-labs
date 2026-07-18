"""Terminal formatting helpers: screen clearing and colorized, typed output."""

import os
import sys
import time

from constants import COLOR_AGENT, COLOR_RESET, COLOR_USER, TYPING_DELAY_SECONDS


def clear_screen() -> None:
    """Clear the terminal, on both POSIX and Windows."""
    os.system("cls" if os.name == "nt" else "clear")


def type_out(text: str, color: str | None = None, delay: float = TYPING_DELAY_SECONDS) -> None:
    """Print text character-by-character to simulate a typed response."""
    prefix, reset = (color, COLOR_RESET) if color else ("", "")
    sys.stdout.write(prefix)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if delay:
            time.sleep(delay)
    sys.stdout.write(f"{reset}\n")


def say(speaker: str, text: str, color: str | None = None) -> None:
    """Print a labeled line of dialogue, e.g. 'Agent: Hello there.'"""
    type_out(f"{speaker}: {text}", color=color)


def ask_caller(question: str) -> str:
    """Print an agent question, then prompt for and return the caller's typed reply."""
    say("Agent", question, color=COLOR_AGENT)
    reply = input(f"{COLOR_USER}You: {COLOR_RESET}")
    return reply.strip()


def read_caller_message() -> str:
    """Prompt for a caller message without a preceding agent question."""
    reply = input(f"{COLOR_USER}You: {COLOR_RESET}")
    return reply.strip()

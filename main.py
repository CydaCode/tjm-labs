"""Entry point: clears the screen, prints the header, and starts the inbound call."""

from agent import InboundSalesAgent
from constants import APP_HEADER
from utils import clear_screen


def main() -> None:
    """Launch the simulated inbound pharmacy sales call."""
    clear_screen()
    print(APP_HEADER)
    print()
    try:
        InboundSalesAgent().run()
    except (KeyboardInterrupt, EOFError):
        print("\nCall ended.")


if __name__ == "__main__":
    main()

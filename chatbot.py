"""CLI entry point for the enhanced Q&A chatbot."""

from __future__ import annotations

import argparse

from backend.chatbot_core import ChatbotConfig, EnhancedQAChatbot


def run_chatbot(name: str, kb_path: str | None) -> None:
    bot = EnhancedQAChatbot(ChatbotConfig(name=name, kb_path=kb_path))
    print(f"{name}: Ready. Type 'exit' to quit.")

    while True:
        user = input("You: ").strip()
        if user.lower() in {"exit", "quit"}:
            print(f"{name}: Goodbye!")
            break

        response = bot.respond(user)
        print(f"{name}: {response}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an enhanced Q&A chatbot.")
    parser.add_argument("--name", default="QABuddy", help="Bot display name")
    parser.add_argument(
        "--kb",
        default=None,
        help="Optional path to a text knowledge-base file (one fact/snippet per line)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_chatbot(name=args.name, kb_path=args.kb)

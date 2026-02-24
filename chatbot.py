"""Simple Q&A-enhancing chatbot.

Features:
- Rule-based intent handling for common conversational needs.
- Context-aware response enhancement (clarifying questions, summaries, and suggestions).
- Optional local knowledge-base lookup from a plain-text file.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class ChatbotConfig:
    name: str = "QABuddy"
    kb_path: str | None = None


@dataclass
class ConversationState:
    history: List[Dict[str, str]] = field(default_factory=list)


class EnhancedQAChatbot:
    def __init__(self, config: ChatbotConfig):
        self.config = config
        self.state = ConversationState()
        self.knowledge_base = self._load_kb(config.kb_path) if config.kb_path else ""

    def _load_kb(self, kb_path: str) -> str:
        path = Path(kb_path)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _retrieve_from_kb(self, question: str) -> str | None:
        if not self.knowledge_base:
            return None

        keywords = [w.lower() for w in re.findall(r"[A-Za-z0-9_]+", question) if len(w) > 3]
        if not keywords:
            return None

        lines = [line.strip() for line in self.knowledge_base.splitlines() if line.strip()]
        ranked = []
        for line in lines:
            score = sum(1 for kw in keywords if kw in line.lower())
            if score > 0:
                ranked.append((score, line))

        if not ranked:
            return None

        ranked.sort(reverse=True)
        return ranked[0][1]

    def _enhance_answer(self, user_input: str, draft_answer: str) -> str:
        follow_up = ""

        if any(token in user_input.lower() for token in ["how", "why", "explain"]):
            follow_up = "\nTip: I can also break this into step-by-step actions if you want."
        elif any(token in user_input.lower() for token in ["what", "define", "meaning"]):
            follow_up = "\nWould you like a short example to make this clearer?"

        return f"{draft_answer}{follow_up}"

    def _base_response(self, user_input: str) -> str:
        text = user_input.lower().strip()

        if any(greet in text for greet in ["hello", "hi", "hey"]):
            return f"Hello! I'm {self.config.name}. Ask me a question and I'll try to improve the answer quality."

        if "help" in text:
            return (
                "I can help by:\n"
                "1) Answering general questions\n"
                "2) Using a local knowledge base if provided\n"
                "3) Suggesting follow-up prompts for clearer understanding"
            )

        kb_answer = self._retrieve_from_kb(user_input)
        if kb_answer:
            return f"From local knowledge base: {kb_answer}"

        return (
            "Here is a structured answer:\n"
            "- Core idea: Break the problem into smaller parts.\n"
            "- Best practice: Verify assumptions and validate with examples.\n"
            "- Next step: Share your exact question for a more targeted answer."
        )

    def respond(self, user_input: str) -> str:
        draft = self._base_response(user_input)
        final = self._enhance_answer(user_input, draft)
        self.state.history.append({"user": user_input, "bot": final})
        return final


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

"""Reusable chatbot core logic for API and CLI use."""

from __future__ import annotations

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

    def _base_response(self, user_input: str, use_kb: bool = True) -> str:
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

        if use_kb:
            kb_answer = self._retrieve_from_kb(user_input)
            if kb_answer:
                return f"From local knowledge base: {kb_answer}"

        return (
            "Here is a structured answer:\n"
            "- Core idea: Break the problem into smaller parts.\n"
            "- Best practice: Verify assumptions and validate with examples.\n"
            "- Next step: Share your exact question for a more targeted answer."
        )

    def respond(self, user_input: str, tools: set[str] | None = None) -> str:
        active_tools = tools or {"knowledge_base", "answer_enhancer"}
        draft = self._base_response(user_input, use_kb="knowledge_base" in active_tools)
        final = self._enhance_answer(user_input, draft) if "answer_enhancer" in active_tools else draft
        self.state.history.append({"user": user_input, "bot": final})
        return final

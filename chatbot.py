"""Simple Q&A-enhancing chatbot.

Features:
- Rule-based intent handling for common conversational needs.
- Context-aware response enhancement (clarifying questions, summaries, and suggestions).
- Optional local knowledge-base lookup from a plain-text file.
"""

from __future__ import annotations

import argparse
import re
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import ttk
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
        final = (
            self._enhance_answer(user_input, draft)
            if "answer_enhancer" in active_tools
            else draft
        )
        self.state.history.append({"user": user_input, "bot": final})
        return final


class ChatbotUI:
    TOOL_OPTIONS = {
        "knowledge_base": "Knowledge Base Lookup",
        "answer_enhancer": "Answer Enhancer",
    }

    def __init__(self, bot: EnhancedQAChatbot):
        self.bot = bot
        self.root = tk.Tk()
        self.root.title(f"{bot.config.name} UI")
        self.root.geometry("760x560")

        self.tool_vars: Dict[str, tk.BooleanVar] = {
            key: tk.BooleanVar(value=True) for key in self.TOOL_OPTIONS
        }

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        title = ttk.Label(
            self.root,
            text=f"{self.bot.config.name} - Enhanced Q&A",
            font=("Arial", 15, "bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        container = ttk.Frame(self.root)
        container.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self.chat_log = tk.Text(container, wrap="word", state="disabled")
        self.chat_log.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tools_frame = ttk.LabelFrame(container, text="Select tools")
        tools_frame.grid(row=0, column=1, sticky="ns")
        for i, (tool_key, label) in enumerate(self.TOOL_OPTIONS.items()):
            ttk.Checkbutton(
                tools_frame,
                text=label,
                variable=self.tool_vars[tool_key],
            ).grid(row=i, column=0, sticky="w", padx=10, pady=8)

        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 12))
        input_frame.columnconfigure(0, weight=1)

        self.user_input = ttk.Entry(input_frame)
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.user_input.bind("<Return>", self._on_send)

        send_btn = ttk.Button(input_frame, text="Send", command=self._on_send)
        send_btn.grid(row=0, column=1)

        self._append_message(
            self.bot.config.name,
            "Ready. Enter a question and pick tools from the panel.",
        )

    def _selected_tools(self) -> set[str]:
        return {name for name, enabled in self.tool_vars.items() if enabled.get()}

    def _append_message(self, sender: str, message: str) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", f"{sender}: {message}\n\n")
        self.chat_log.see("end")
        self.chat_log.configure(state="disabled")

    def _on_send(self, _event=None) -> None:
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self.user_input.delete(0, "end")
        self._append_message("You", user_text)

        response = self.bot.respond(user_text, tools=self._selected_tools())
        self._append_message(self.bot.config.name, response)

    def run(self) -> None:
        self.root.mainloop()


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
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch a desktop UI where users can enter prompts and select tools",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.ui:
        ChatbotUI(EnhancedQAChatbot(ChatbotConfig(name=args.name, kb_path=args.kb))).run()
    else:
        run_chatbot(name=args.name, kb_path=args.kb)

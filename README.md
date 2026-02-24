# Python Enhanced Q&A Chatbot

A lightweight Python chatbot that improves question-and-answer interactions by:

- Giving structured answers
- Suggesting useful follow-up prompts
- Optionally retrieving relevant lines from a local knowledge-base text file

## Run

```bash
python3 chatbot.py
```

Optional arguments:

```bash
python3 chatbot.py --name HelperBot --kb knowledge.txt
python3 chatbot.py --ui
```

Use `--ui` to open a desktop interface where users can enter prompts and enable/disable chatbot tools (Knowledge Base Lookup and Answer Enhancer).

## Example `knowledge.txt`

```text
Python is an interpreted, high-level programming language.
A chatbot can improve support efficiency by handling common questions instantly.
```

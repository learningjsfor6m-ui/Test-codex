from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.chatbot_core import ChatbotConfig, EnhancedQAChatbot

app = Flask(__name__)
CORS(app)

bot = EnhancedQAChatbot(ChatbotConfig(name="QABuddy", kb_path=None))


@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})


@app.post('/api/chat')
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get('message') or '').strip()
    tools = payload.get('tools') or ["knowledge_base", "answer_enhancer"]

    if not message:
        return jsonify({'error': 'message is required'}), 400

    response = bot.respond(message, tools=set(tools))
    return jsonify({'response': response, 'history': bot.state.history})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

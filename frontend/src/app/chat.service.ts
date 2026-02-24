import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly apiBase = 'http://localhost:5000/api';

  async sendMessage(message: string, tools: string[]): Promise<string> {
    const response = await fetch(`${this.apiBase}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, tools })
    });

    if (!response.ok) {
      throw new Error('Failed to reach chatbot API');
    }

    const data = (await response.json()) as { response: string };
    return data.response;
  }
}

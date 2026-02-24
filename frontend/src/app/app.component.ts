import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService } from './chat.service';

type Message = { sender: 'You' | 'QABuddy'; text: string };

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  userInput = '';
  loading = false;
  useKnowledgeBase = true;
  useEnhancer = true;
  messages: Message[] = [
    { sender: 'QABuddy', text: 'Ready. Enter a question and pick tools from the panel.' }
  ];

  constructor(private readonly chatService: ChatService) {}

  async send(): Promise<void> {
    const content = this.userInput.trim();
    if (!content || this.loading) {
      return;
    }

    this.messages.push({ sender: 'You', text: content });
    this.userInput = '';
    this.loading = true;

    const tools = [
      ...(this.useKnowledgeBase ? ['knowledge_base'] : []),
      ...(this.useEnhancer ? ['answer_enhancer'] : [])
    ];

    try {
      const reply = await this.chatService.sendMessage(content, tools);
      this.messages.push({ sender: 'QABuddy', text: reply });
    } catch (error) {
      this.messages.push({ sender: 'QABuddy', text: 'Sorry, I could not reach the Python backend.' });
    } finally {
      this.loading = false;
    }
  }
}

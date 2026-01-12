import { useState, useCallback } from 'react';
import { streamChat } from '@/api/ollama';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export function useStreamingChat(model: string, systemPrompt?: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);
    setCurrentResponse('');
    setError(null);

    try {
      let fullResponse = '';
      for await (const chunk of streamChat(model, content, systemPrompt)) {
        fullResponse += chunk;
        setCurrentResponse(fullResponse);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: fullResponse,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      console.error('Chat error:', err);
    } finally {
      setIsStreaming(false);
      setCurrentResponse('');
    }
  }, [model, systemPrompt]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { 
    messages, 
    sendMessage, 
    isStreaming, 
    currentResponse, 
    error,
    clearMessages 
  };
}

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function sendMessageToAPI(message: string): Promise<string> {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    return data.response || data.error || 'No response';
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('fetch')) {
        throw new Error('Cannot connect to API. Is the backend running?');
      }
      throw error;
    }
    throw new Error('Unknown error');
  }
}

function ChatMessage({ role, content, timestamp }: Message) {
  const isUser = role === 'user';
  
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center shrink-0
        ${isUser ? 'bg-accent-gold/20 text-accent-gold' : 'bg-bg-tertiary text-text-secondary'}
      `}>
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      
      <div className={`
        max-w-[80%] rounded-lg px-4 py-3
        ${isUser 
          ? 'bg-accent-gold/10 border border-accent-gold/20' 
          : 'bg-bg-card border border-bg-tertiary'
        }
      `}>
        <p className="text-text-primary whitespace-pre-wrap">{content}</p>
        <p className="text-xs text-text-secondary mt-2">
          {new Date(timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const userMessage = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: Date.now(),
    }]);
    
    setLoading(true);
    try {
      const response = await sendMessageToAPI(userMessage);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response,
        timestamp: Date.now(),
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="flex flex-col h-full bg-bg-card rounded-xl overflow-hidden">
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-text-secondary py-12">
            <p className="text-lg">Start a conversation with the AI</p>
            <p className="text-sm mt-2">Ask about deck optimization, card prices, or synergies</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <ChatMessage key={i} {...msg} />
        ))}
        
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-bg-tertiary flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin text-text-secondary" />
            </div>
            <div className="bg-bg-card border border-bg-tertiary rounded-lg px-4 py-3">
              <span className="text-text-secondary">Thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="border-t border-bg-tertiary p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something about your collection..."
            disabled={loading}
            className="flex-1 bg-bg-secondary text-text-primary px-4 py-3 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-accent-gold/50
                       disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-accent-gold text-bg-primary px-4 py-3 rounded-lg
                       hover:bg-accent-gold/90 transition disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Circle } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

type ConnectionStatus = 'checking' | 'ollama' | 'backend' | 'offline';

const OLLAMA_URL = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_MODEL = 'llama3.2:3b';

const SYSTEM_PROMPT = `You are CardForge AI, an expert Magic: The Gathering assistant. You help users with:
- Deck building and optimization
- Card synergies and combos
- Rules questions and interactions
- Collection management advice
- Meta analysis and strategy

Be concise but helpful. Use MTG terminology appropriately.`;

async function checkOllamaStatus(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const response = await fetch(`${OLLAMA_URL}/api/tags`, { 
      signal: controller.signal 
    });
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

async function checkBackendStatus(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const response = await fetch(`${API_URL}/health`, { 
      signal: controller.signal 
    });
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

async function sendToOllama(message: string, model: string = DEFAULT_MODEL): Promise<string> {
  const response = await fetch(`${OLLAMA_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model,
      prompt: message,
      system: SYSTEM_PROMPT,
      stream: false,
    }),
  });

  if (!response.ok) {
    throw new Error(`Ollama error: ${response.status}`);
  }

  const data = await response.json();
  return data.response || 'No response from model';
}

async function sendToBackendAPI(message: string): Promise<string> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  
  if (!response.ok) {
    throw new Error(`Backend API error: ${response.status}`);
  }
  
  const data = await response.json();
  return data.response || data.error || 'No response';
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

function ConnectionIndicator({ status }: { status: ConnectionStatus }) {
  const statusConfig = {
    checking: { color: 'text-yellow-500', fill: 'fill-yellow-500', label: 'Checking...' },
    ollama: { color: 'text-green-500', fill: 'fill-green-500', label: 'Ollama (Local)' },
    backend: { color: 'text-blue-500', fill: 'fill-blue-500', label: 'Backend API' },
    offline: { color: 'text-red-500', fill: 'fill-red-500', label: 'Offline' },
  };
  
  const config = statusConfig[status];
  
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-bg-tertiary/50 rounded-full text-xs">
      <Circle className={`w-2 h-2 ${config.color} ${config.fill}`} />
      <span className={config.color}>{config.label}</span>
    </div>
  );
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('checking');
  const [ollamaAvailable, setOllamaAvailable] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    async function checkConnections() {
      setConnectionStatus('checking');
      
      const [ollama, backend] = await Promise.all([
        checkOllamaStatus(),
        checkBackendStatus(),
      ]);
      
      setOllamaAvailable(ollama);
      setBackendAvailable(backend);
      
      if (ollama) {
        setConnectionStatus('ollama');
      } else if (backend) {
        setConnectionStatus('backend');
      } else {
        setConnectionStatus('offline');
      }
    }
    
    checkConnections();
    const interval = setInterval(checkConnections, 30000);
    return () => clearInterval(interval);
  }, []);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    if (connectionStatus === 'offline') return;
    
    const userMessage = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: Date.now(),
    }]);
    
    setLoading(true);
    try {
      let response: string;
      
      if (ollamaAvailable) {
        try {
          response = await sendToOllama(userMessage);
        } catch (ollamaError) {
          console.warn('Ollama failed, trying backend:', ollamaError);
          if (backendAvailable) {
            response = await sendToBackendAPI(userMessage);
          } else {
            throw ollamaError;
          }
        }
      } else if (backendAvailable) {
        response = await sendToBackendAPI(userMessage);
      } else {
        throw new Error('No AI service available');
      }
      
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
  
  const isDisabled = loading || connectionStatus === 'offline' || connectionStatus === 'checking';
  
  return (
    <div className="flex flex-col h-full bg-bg-card rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-bg-tertiary">
        <span className="text-sm text-text-secondary">CardForge AI</span>
        <ConnectionIndicator status={connectionStatus} />
      </div>
      
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-text-secondary py-12">
            <p className="text-lg">Start a conversation with the AI</p>
            <p className="text-sm mt-2">Ask about deck optimization, card prices, or synergies</p>
            {connectionStatus === 'offline' && (
              <p className="text-sm mt-4 text-red-400">
                No AI service available. Start Ollama locally or ensure backend is running.
              </p>
            )}
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
            placeholder={connectionStatus === 'offline' ? 'AI offline - start Ollama or backend' : 'Ask something about your collection...'}
            disabled={isDisabled}
            className="flex-1 bg-bg-secondary text-text-primary px-4 py-3 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-accent-gold/50
                       disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isDisabled || !input.trim()}
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

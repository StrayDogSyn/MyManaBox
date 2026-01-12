import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { streamChat } from '../../api/ollama';
import { useAvailableModels } from '../../api/hooks/useAgents';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatWindow() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: models } = useAvailableModels();

  // Set default model when loaded
  useEffect(() => {
    if (models && models.length > 0 && !selectedModel) {
      // Prefer llama3.2:3b or first available
      const defaultModel = models.find(m => m.name.includes('llama3.2'))?.name || models[0].name;
      setSelectedModel(defaultModel);
    }
  }, [models, selectedModel]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedModel || isLoading) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Add empty assistant message
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      const stream = streamChat(selectedModel, userMessage);
      
      let fullResponse = '';
      for await (const chunk of stream) {
        fullResponse += chunk;
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMsg = newMessages[newMessages.length - 1];
          if (lastMsg.role === 'assistant') {
            lastMsg.content = fullResponse;
          }
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Failed to generate response. Is Ollama running?' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-bg-secondary rounded-lg border border-bg-tertiary overflow-hidden">
      {/* Header with Model Selector */}
      <div className="p-3 border-b border-bg-tertiary flex justify-between items-center bg-bg-tertiary/30">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Bot size={16} />
          <span className="font-medium text-white">AI Assistant</span>
        </div>
        <select 
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="bg-bg-primary border border-bg-tertiary rounded px-2 py-1 text-xs text-white focus:border-accent-gold outline-none"
        >
          <option value="" disabled>Select Model</option>
          {models?.map(m => (
            <option key={m.name} value={m.name}>{m.name}</option>
          ))}
        </select>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 opacity-50">
            <Bot size={48} className="mb-2" />
            <p>Select a model and start chatting!</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={clsx("flex gap-3", msg.role === 'user' ? "flex-row-reverse" : "")}>
            <div className={clsx(
              "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
              msg.role === 'user' ? "bg-accent-gold/20 text-accent-gold" : "bg-purple-500/20 text-purple-400"
            )}>
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className={clsx(
              "p-3 rounded-lg max-w-[85%] text-sm leading-relaxed whitespace-pre-wrap",
              msg.role === 'user' ? "bg-accent-gold/10 text-white" : "bg-bg-tertiary text-gray-200"
            )}>
              {msg.content}
              {msg.role === 'assistant' && isLoading && i === messages.length - 1 && (
                <span className="inline-block w-1.5 h-4 ml-1 bg-purple-400 animate-pulse align-middle" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t border-bg-tertiary bg-bg-secondary">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSend()}
            placeholder={isLoading ? "Generating..." : "Ask AI about your deck..."}
            disabled={isLoading || !selectedModel}
            className="w-full bg-black/20 border border-bg-tertiary rounded-lg pl-4 pr-12 py-3 text-white focus:border-accent-gold focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim() || !selectedModel}
            className="absolute right-2 top-2 p-1.5 bg-accent-gold/20 text-accent-gold rounded-md hover:bg-accent-gold/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>
      </div>
    </div>
  );
}

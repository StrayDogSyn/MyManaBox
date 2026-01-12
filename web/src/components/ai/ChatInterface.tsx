import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { ChatMessage } from './ChatMessage';
import { AgentSelector } from './AgentSelector';
import { useStreamingChat } from './useStreamingChat';
import { useOllamaStatus } from '@/api/hooks';

interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  system_prompt: string;
}

const DEFAULT_AGENTS: Agent[] = [
  {
    id: 'deck-advisor',
    name: 'Deck Advisor',
    description: 'Helps optimize your deck composition and strategy',
    model: 'llama3.2:3b',
    system_prompt: 'You are an expert MTG deck advisor. Help users optimize their decks, suggest cards, and explain strategy.',
  },
  {
    id: 'rules-expert',
    name: 'Rules Expert',
    description: 'Answers questions about MTG rules and interactions',
    model: 'llama3.2:3b',
    system_prompt: 'You are an MTG rules expert. Answer questions about game rules, card interactions, and tournament procedures accurately.',
  },
  {
    id: 'collection-manager',
    name: 'Collection Manager',
    description: 'Helps organize and value your card collection',
    model: 'llama3.2:3b',
    system_prompt: 'You are a collection management assistant. Help users organize, value, and track their MTG card collections.',
  },
];

export function ChatInterface() {
  const [selectedAgent, setSelectedAgent] = useState<Agent>(DEFAULT_AGENTS[0]);
  const [input, setInput] = useState('');
  const [streamingTimestamp] = useState(() => Date.now());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleAgentSelect = (agent: { id: string; name: string; description: string; model: string }) => {
    const fullAgent = DEFAULT_AGENTS.find(a => a.id === agent.id);
    if (fullAgent) setSelectedAgent(fullAgent);
  };

  const { data: isOnline = false } = useOllamaStatus();
  const { 
    messages, 
    sendMessage, 
    isStreaming, 
    currentResponse, 
    error,
    clearMessages 
  } = useStreamingChat(selectedAgent.model, selectedAgent.system_prompt);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentResponse]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-bg-secondary rounded-lg border border-bg-tertiary overflow-hidden">
      <div className="flex items-center justify-between p-3 border-b border-bg-tertiary">
        <AgentSelector
          agents={DEFAULT_AGENTS}
          selectedAgent={selectedAgent}
          onSelect={handleAgentSelect}
          isOnline={isOnline}
        />
        <button
          onClick={clearMessages}
          className="p-2 text-gray-400 hover:text-white hover:bg-bg-hover rounded-lg transition-colors"
          title="Clear chat"
        >
          <Trash2 size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <div className="text-4xl mb-4">🎴</div>
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-1">
              Ask {selectedAgent.name} about your MTG collection or decks
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage
            key={i}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))}

        {isStreaming && currentResponse && (
          <ChatMessage
            role="assistant"
            content={currentResponse}
            timestamp={streamingTimestamp}
            isStreaming
          />
        )}

        {isStreaming && !currentResponse && (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-accent-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-accent-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-accent-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
            <AlertCircle size={18} />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-bg-tertiary">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isOnline ? `Ask ${selectedAgent.name}...` : 'Ollama is offline...'}
            disabled={!isOnline || isStreaming}
            className={clsx(
              "w-full bg-bg-primary border border-bg-tertiary rounded-lg pl-4 pr-12 py-3 text-white placeholder-gray-500 transition-colors",
              "focus:outline-none focus:ring-1 focus:ring-accent-gold focus:border-accent-gold",
              (!isOnline || isStreaming) && "opacity-50 cursor-not-allowed"
            )}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming || !isOnline}
            className={clsx(
              "absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-colors",
              input.trim() && !isStreaming && isOnline
                ? "bg-accent-gold text-black hover:bg-accent-gold/80"
                : "bg-bg-tertiary text-gray-500 cursor-not-allowed"
            )}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

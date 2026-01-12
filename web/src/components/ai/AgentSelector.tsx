import { ChevronDown, Bot, Cpu } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';

interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
}

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onSelect: (agent: Agent) => void;
  isOnline: boolean;
}

const MODEL_BADGES: Record<string, { label: string; color: string }> = {
  'llama3.2:3b': { label: '3B', color: 'bg-green-500/20 text-green-400' },
  'llama3.1:8b': { label: '8B', color: 'bg-blue-500/20 text-blue-400' },
  'llama3.1:70b': { label: '70B', color: 'bg-purple-500/20 text-purple-400' },
  'mistral:7b': { label: '7B', color: 'bg-orange-500/20 text-orange-400' },
  'codellama:7b': { label: '7B', color: 'bg-cyan-500/20 text-cyan-400' },
};

function getModelBadge(model: string) {
  return MODEL_BADGES[model] || { label: model.split(':')[1] || 'AI', color: 'bg-gray-500/20 text-gray-400' };
}

export function AgentSelector({ agents, selectedAgent, onSelect, isOnline }: AgentSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-bg-tertiary border border-bg-hover rounded-lg hover:bg-bg-hover transition-colors"
      >
        <Bot size={18} className="text-accent-blue" />
        <span className="text-white text-sm">
          {selectedAgent?.name || 'Select Agent'}
        </span>
        <div className={clsx(
          "w-2 h-2 rounded-full",
          isOnline ? "bg-green-500" : "bg-red-500"
        )} />
        <ChevronDown size={16} className={clsx(
          "text-gray-400 transition-transform",
          isOpen && "rotate-180"
        )} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 bg-bg-secondary border border-bg-tertiary rounded-lg shadow-xl z-50 overflow-hidden">
          <div className="p-2 border-b border-bg-tertiary">
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Cpu size={12} />
              <span>Ollama Status:</span>
              <span className={isOnline ? "text-green-400" : "text-red-400"}>
                {isOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>

          <div className="max-h-64 overflow-y-auto">
            {agents.map((agent) => {
              const badge = getModelBadge(agent.model);
              return (
                <button
                  key={agent.id}
                  onClick={() => {
                    onSelect(agent);
                    setIsOpen(false);
                  }}
                  className={clsx(
                    "w-full p-3 text-left hover:bg-bg-hover transition-colors",
                    selectedAgent?.id === agent.id && "bg-bg-tertiary"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">{agent.name}</span>
                    <span className={clsx("text-xs px-2 py-0.5 rounded", badge.color)}>
                      {badge.label}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{agent.description}</p>
                </button>
              );
            })}
          </div>

          {agents.length === 0 && (
            <div className="p-4 text-center text-gray-500 text-sm">
              No agents available
            </div>
          )}
        </div>
      )}
    </div>
  );
}

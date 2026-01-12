import { Search, Bell, User, Circle } from 'lucide-react';
import { useOllamaStatus } from '../../api/hooks/useAgents';
import clsx from 'clsx';

interface HeaderProps {
  sidebarCollapsed: boolean;
}

export function Header({ sidebarCollapsed }: HeaderProps) {
  const { data: isOllamaConnected } = useOllamaStatus();

  return (
    <header 
      className={clsx(
        "h-16 bg-bg-secondary border-b border-bg-tertiary flex items-center justify-between px-6 sticky top-0 z-10 transition-all duration-300",
        sidebarCollapsed ? "ml-16" : "ml-64"
      )}
    >
      <div className="flex items-center gap-4 flex-1">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            type="text"
            placeholder="Search cards, decks..."
            className="w-full bg-bg-tertiary border border-bg-hover rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-accent-gold focus:border-accent-gold transition-colors"
          />
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-bg-tertiary/50 border border-bg-tertiary text-xs">
          <Circle size={8} className={isOllamaConnected ? "fill-green-500 text-green-500" : "fill-red-500 text-red-500"} />
          <span className={isOllamaConnected ? "text-green-500" : "text-red-500"}>
            Ollama {isOllamaConnected ? "Online" : "Offline"}
          </span>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <button className="p-2 text-gray-400 hover:text-white hover:bg-bg-hover rounded-lg transition-colors">
          <Bell size={20} />
        </button>
        <div className="w-8 h-8 rounded-full bg-accent-gold/20 flex items-center justify-center text-accent-gold cursor-pointer hover:bg-accent-gold/30 transition-colors">
          <User size={18} />
        </div>
      </div>
    </header>
  );
}

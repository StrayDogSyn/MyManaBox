import { ChatInterface } from '@/components/ai/ChatInterface';
import { Database, Layers, Sparkles } from 'lucide-react';

export function AIWorkspace() {
  return (
    <div className="h-[calc(100vh-64px-48px)] flex gap-6">
      <div className="flex-1 min-w-0">
        <ChatInterface />
      </div>

      <div className="w-80 flex flex-col gap-4 shrink-0">
        <div className="bg-bg-secondary rounded-lg border border-bg-tertiary p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Database size={16} />
            Collection Summary
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Cards</span>
              <span className="text-white">--</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Unique Cards</span>
              <span className="text-white">--</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Est. Value</span>
              <span className="text-accent-gold">--</span>
            </div>
          </div>
        </div>

        <div className="bg-bg-secondary rounded-lg border border-bg-tertiary p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Layers size={16} />
            Selected Deck
          </h3>
          <p className="text-sm text-gray-500 italic">No deck selected</p>
          <button className="mt-3 w-full py-2 px-3 bg-bg-tertiary hover:bg-bg-hover text-gray-300 text-sm rounded-lg transition-colors">
            Select a Deck
          </button>
        </div>

        <div className="bg-bg-secondary rounded-lg border border-bg-tertiary p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Sparkles size={16} />
            Quick Actions
          </h3>
          <div className="space-y-2">
            <button className="w-full py-2 px-3 bg-accent-gold/10 hover:bg-accent-gold/20 text-accent-gold text-sm rounded-lg transition-colors text-left">
              Analyze my collection
            </button>
            <button className="w-full py-2 px-3 bg-accent-blue/10 hover:bg-accent-blue/20 text-accent-blue text-sm rounded-lg transition-colors text-left">
              Suggest deck improvements
            </button>
            <button className="w-full py-2 px-3 bg-bg-tertiary hover:bg-bg-hover text-gray-300 text-sm rounded-lg transition-colors text-left">
              Find similar cards
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

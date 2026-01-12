import { ChatWindow } from './ChatWindow';

export function StrategySession() {
  return (
    <div className="flex h-full gap-6">
      <div className="w-2/3 bg-bg-secondary rounded-lg border border-bg-tertiary p-4">
        <h2 className="text-xl font-bold text-white mb-4">Deck Visualization</h2>
        {/* Placeholder for graphs/charts */}
        <div className="h-64 bg-black/20 rounded-lg flex items-center justify-center text-gray-500">
          Mana Curve Chart
        </div>
        <div className="mt-4 h-64 bg-black/20 rounded-lg flex items-center justify-center text-gray-500">
          Type Distribution
        </div>
      </div>
      
      <div className="w-1/3">
        <ChatWindow />
      </div>
    </div>
  );
}

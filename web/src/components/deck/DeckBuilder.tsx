import { useState } from 'react';
import { CardGrid } from '../cards/CardGrid';

export function DeckBuilder() {
  const [deckName, setDeckName] = useState("New Deck");
  const [cards] = useState<unknown[]>([]);

  return (
    <div className="flex h-full gap-6">
      <div className="w-1/2 flex flex-col">
        <div className="mb-4">
          <input 
            type="text" 
            value={deckName}
            onChange={(e) => setDeckName(e.target.value)}
            className="text-2xl font-bold bg-transparent border-none focus:ring-0 text-white w-full"
          />
        </div>
        
        <div className="flex-1 bg-bg-secondary rounded-lg border border-bg-tertiary p-4 overflow-y-auto">
          <h3 className="text-gray-400 mb-2">Mainboard ({cards.length})</h3>
          {/* Deck list goes here */}
          {cards.length === 0 && (
            <div className="text-center text-gray-500 mt-10">
              Drag cards here to build your deck
            </div>
          )}
        </div>
      </div>
      
      <div className="w-1/2 flex flex-col">
        {/* Search and Card Pool */}
        <div className="mb-4">
          <input 
            type="text" 
            placeholder="Search cards..." 
            className="w-full bg-bg-secondary border border-bg-tertiary rounded-lg px-4 py-2 text-white"
          />
        </div>
        <div className="flex-1 overflow-y-auto">
          <CardGrid cards={[]} /> 
        </div>
      </div>
    </div>
  );
}

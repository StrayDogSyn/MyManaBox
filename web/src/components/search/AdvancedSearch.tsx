import { Search } from 'lucide-react';

export function AdvancedSearch() {
  return (
    <div className="bg-bg-secondary p-4 rounded-lg border border-bg-tertiary">
      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={20} />
          <input 
            type="text" 
            placeholder="Search cards..." 
            className="w-full bg-black/20 border border-bg-tertiary rounded-lg pl-10 pr-4 py-2 text-white focus:border-accent-gold focus:outline-none"
          />
        </div>
        <button className="bg-accent-gold/20 text-accent-gold px-4 py-2 rounded-lg hover:bg-accent-gold/30">
          Filters
        </button>
      </div>
      
      {/* Filter Chips */}
      <div className="flex gap-2 flex-wrap">
        {['White', 'Blue', 'Black', 'Red', 'Green'].map((color) => (
          <button key={color} className="px-3 py-1 rounded-full bg-bg-tertiary text-sm text-gray-300 hover:bg-white/10">
            {color}
          </button>
        ))}
      </div>
    </div>
  );
}

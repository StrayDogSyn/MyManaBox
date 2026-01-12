import { X } from 'lucide-react';

interface CardDetailsProps {
  card: {
    id: string;
    name: string;
    mana_cost?: string;
    type_line?: string;
    oracle_text?: string;
    imageUrl?: string;
    price?: number;
  };
  onClose: () => void;
}

export function CardDetails({ card, onClose }: CardDetailsProps) {
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-bg-secondary rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-bg-tertiary flex flex-col md:flex-row">
        <div className="p-6 md:w-1/3">
          <img 
            src={card.imageUrl} 
            alt={card.name} 
            className="w-full rounded-lg shadow-xl"
          />
        </div>
        <div className="p-6 md:w-2/3 relative">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
          
          <h2 className="text-3xl font-bold text-white mb-2">{card.name}</h2>
          <div className="text-lg text-gray-300 mb-4">{card.mana_cost}</div>
          <div className="text-xl font-medium text-accent-gold mb-4">{card.type_line}</div>
          
          <div className="bg-black/20 p-4 rounded-lg mb-6">
            <p className="text-gray-200 whitespace-pre-wrap">{card.oracle_text}</p>
          </div>
          
          {card.price && (
            <div className="text-2xl font-bold text-green-400">
              ${card.price.toFixed(2)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

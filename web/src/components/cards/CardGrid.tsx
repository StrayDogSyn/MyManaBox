import { CardCard } from './CardCard';

interface CardGridProps {
  cards: Array<{ id: string; name: string; set: string; price?: number; imageUrl?: string }>;
  onCardClick?: (id: string) => void;
}

export function CardGrid({ cards, onCardClick }: CardGridProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {cards.map((card) => (
        <CardCard 
          key={card.id} 
          {...card} 
          onClick={() => onCardClick?.(card.id)} 
        />
      ))}
    </div>
  );
}

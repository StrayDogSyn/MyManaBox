
interface CardProps {
  name: string;
  set: string;
  price?: number;
  imageUrl?: string;
  onClick?: () => void;
}

export function CardCard({ name, set, price, imageUrl, onClick }: CardProps) {
  return (
    <div 
      className="bg-bg-secondary rounded-lg overflow-hidden border border-bg-tertiary hover:border-accent-gold transition-colors cursor-pointer"
      onClick={onClick}
    >
      <div className="aspect-[2.5/3.5] bg-black/50 relative">
        {imageUrl ? (
          <img src={imageUrl} alt={name} className="w-full h-full object-cover" />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No Image
          </div>
        )}
      </div>
      <div className="p-3">
        <h3 className="font-medium text-white truncate">{name}</h3>
        <div className="flex justify-between items-center mt-1 text-sm text-gray-400">
          <span className="uppercase">{set}</span>
          {price && <span className="text-green-400">${price.toFixed(2)}</span>}
        </div>
      </div>
    </div>
  );
}

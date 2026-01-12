import { Search, Bell, User } from 'lucide-react';

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  return (
    <header className="h-16 bg-bg-secondary border-b border-bg-tertiary flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {title && <h1 className="text-xl font-semibold">{title}</h1>}
      </div>
      
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            placeholder="Search cards..."
            className="bg-bg-tertiary text-text-primary pl-10 pr-4 py-2 rounded-lg w-64
                       focus:outline-none focus:ring-2 focus:ring-accent-gold/50"
          />
        </div>
        
        <button className="p-2 text-text-secondary hover:text-text-primary transition">
          <Bell className="w-5 h-5" />
        </button>
        
        <button className="p-2 text-text-secondary hover:text-text-primary transition">
          <User className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}

import { Library, Layers, Bot, Settings, ChevronLeft, ChevronRight, TrendingUp, Swords } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { icon: Library, label: 'Collection', path: '/collection' },
  { icon: Layers, label: 'Decks', path: '/decks' },
  { icon: TrendingUp, label: 'Analytics', path: '/analytics' },
  { icon: Bot, label: 'AI Workspace', path: '/ai' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside 
      className={`
        ${collapsed ? 'w-16' : 'w-64'} 
        bg-bg-secondary border-r border-bg-tertiary
        transition-all duration-300 flex flex-col shrink-0
      `}
    >
      <div className="h-16 flex items-center justify-center border-b border-bg-tertiary">
        {collapsed ? (
          <Swords className="w-6 h-6 text-accent-gold" />
        ) : (
          <span className="font-display text-xl text-accent-gold">CardForge</span>
        )}
      </div>
      
      <nav className="flex-1 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 mx-2 rounded-lg
              transition-colors duration-200
              ${isActive 
                ? 'bg-accent-gold/10 text-accent-gold' 
                : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
              }
            `}
          >
            <item.icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
      
      <button
        onClick={onToggle}
        className="h-12 flex items-center justify-center border-t border-bg-tertiary
                   text-text-secondary hover:text-text-primary transition-colors"
      >
        {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
      </button>
    </aside>
  );
}

import { Home, Layers, Database, Bot, Settings, ChevronLeft, ChevronRight, TrendingUp } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import clsx from 'clsx';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  
  const navItems = [
    { icon: Home, label: 'Dashboard', path: '/' },
    { icon: Database, label: 'Collection', path: '/collection' },
    { icon: Layers, label: 'Decks', path: '/decks' },
    { icon: TrendingUp, label: 'Analytics', path: '/analytics' },
    { icon: Bot, label: 'AI Workspace', path: '/ai' },
  ];

  const bottomItems = [
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <aside 
      className={clsx(
        "bg-bg-secondary border-r border-bg-tertiary h-screen fixed left-0 top-0 flex flex-col transition-all duration-300 z-20",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="p-4 border-b border-bg-tertiary flex items-center justify-between min-h-[64px]">
        {collapsed ? (
          <span className="text-2xl mx-auto">⚔️</span>
        ) : (
          <h1 className="text-xl font-display font-bold text-accent-gold">CardForge</h1>
        )}
      </div>
      
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => clsx(
              "flex items-center px-3 py-3 rounded-lg transition-colors",
              collapsed ? "justify-center" : "space-x-3",
              isActive
                ? "bg-accent-gold/10 text-accent-gold border-l-2 border-accent-gold" 
                : "text-gray-400 hover:bg-bg-hover hover:text-white"
            )}
            title={collapsed ? item.label : undefined}
          >
            <item.icon size={20} />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="p-2 border-t border-bg-tertiary space-y-1">
        {bottomItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => clsx(
              "flex items-center px-3 py-3 rounded-lg transition-colors",
              collapsed ? "justify-center" : "space-x-3",
              isActive
                ? "bg-accent-gold/10 text-accent-gold" 
                : "text-gray-400 hover:bg-bg-hover hover:text-white"
            )}
            title={collapsed ? item.label : undefined}
          >
            <item.icon size={20} />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
        
        <button
          onClick={onToggle}
          className="w-full flex items-center px-3 py-3 rounded-lg text-gray-400 hover:bg-bg-hover hover:text-white transition-colors justify-center"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>
    </aside>
  );
}

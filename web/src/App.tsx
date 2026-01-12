import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell } from './components/layout/AppShell';
import { AIWorkspace } from './pages/AIWorkspace';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

function HomePage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="bg-bg-card p-6 rounded-xl">
        <h2 className="text-2xl font-display text-accent-gold mb-2">Collection</h2>
        <p className="text-text-secondary">1,894 cards cataloged</p>
        <p className="text-text-secondary">$2,847.50 total value</p>
      </div>
      <div className="bg-bg-card p-6 rounded-xl">
        <h2 className="text-2xl font-display text-accent-gold mb-2">Decks</h2>
        <p className="text-text-secondary">4 active decks</p>
        <p className="text-text-secondary">Kaalia: 65% win rate</p>
      </div>
      <div className="bg-bg-card p-6 rounded-xl">
        <h2 className="text-2xl font-display text-accent-gold mb-2">AI Status</h2>
        <p className="text-text-secondary">Checking Ollama...</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <AppShell title="Dashboard">
              <HomePage />
            </AppShell>
          } />
          <Route path="/collection" element={
            <AppShell title="Collection">
              <div className="text-text-primary">Collection Page - Coming Soon</div>
            </AppShell>
          } />
          <Route path="/decks" element={
            <AppShell title="Decks">
              <div className="text-text-primary">Decks Page - Coming Soon</div>
            </AppShell>
          } />
          <Route path="/analytics" element={
            <AppShell title="Analytics">
              <div className="text-text-primary">Analytics Page - Coming Soon</div>
            </AppShell>
          } />
          <Route path="/ai" element={
            <AppShell title="AI Workspace">
              <AIWorkspace />
            </AppShell>
          } />
          <Route path="/settings" element={
            <AppShell title="Settings">
              <div className="text-text-primary">Settings Page - Coming Soon</div>
            </AppShell>
          } />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

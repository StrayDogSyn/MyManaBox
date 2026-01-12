import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { AIWorkspace } from './pages/AIWorkspace';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<div className="text-white">Dashboard - Coming Soon</div>} />
            <Route path="/collection" element={<div className="text-white">Collection - Coming Soon</div>} />
            <Route path="/decks" element={<div className="text-white">Decks - Coming Soon</div>} />
            <Route path="/analytics" element={<div className="text-white">Analytics - Coming Soon</div>} />
            <Route path="/ai" element={<AIWorkspace />} />
            <Route path="/settings" element={<div className="text-white">Settings - Coming Soon</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

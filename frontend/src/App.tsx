import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionProvider } from './contexts/SessionContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import Flows from './pages/Flows';
import Validation from './pages/Validation';
import Database from './pages/Database';
import Tools from './pages/Tools';
import Chat from './pages/Chat';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <SessionProvider>
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/flows" element={<Flows />} />
                <Route path="/validation" element={<Validation />} />
                <Route path="/database" element={<Database />} />
                <Route path="/tools" element={<Tools />} />
                <Route path="/chat" element={<Chat />} />
              </Routes>
            </Layout>
          </Router>
        </SessionProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

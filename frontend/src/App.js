import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TechnicalAnalysis from './pages/TechnicalAnalysis';
import AIAnalysis from './pages/AIAnalysis';
import SignalHistory from './pages/SignalHistory';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import { Toaster } from './components/ui/sonner';
import './App.css';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="technical" element={<TechnicalAnalysis />} />
            <Route path="ai-analysis" element={<AIAnalysis />} />
            <Route path="signals" element={<SignalHistory />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </div>
  );
}

export default App;
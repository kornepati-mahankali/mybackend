import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { GemToolProvider } from "./contexts/GemToolContext";
import { SelectedToolProvider } from "./contexts/SelectedToolContext";


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SelectedToolProvider>
      <GemToolProvider>
    <App />
      </GemToolProvider>
    </SelectedToolProvider>
  </StrictMode>
);

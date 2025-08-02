import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { AnimationProvider } from './contexts/AnimationContext';
import { ToolStateProvider } from './contexts/ToolStateContext';
import { SelectedToolProvider } from './contexts/SelectedToolContext';
import { GemToolProvider } from './contexts/GemToolContext';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AnimationProvider>
      <ThemeProvider>
        <AuthProvider>
          <ToolStateProvider>
            <SelectedToolProvider>
              <GemToolProvider>
                <App />
              </GemToolProvider>
            </SelectedToolProvider>
          </ToolStateProvider>
        </AuthProvider>
      </ThemeProvider>
    </AnimationProvider>
  </StrictMode>
);

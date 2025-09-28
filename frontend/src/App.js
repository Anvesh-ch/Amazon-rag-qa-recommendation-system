import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import QATab from './components/QATab';
import RecommendationsTab from './components/RecommendationsTab';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';

// Hooks
import { useAPIHealth } from './hooks/useAPIHealth';

// Theme
const theme = {
  colors: {
    primary: '#FF9900',
    primaryDark: '#E68900',
    secondary: '#232F3E',
    background: '#F8FAFC',
    surface: '#FFFFFF',
    text: '#1E293B',
    textSecondary: '#64748B',
    border: '#E2E8F0',
    success: '#10B981',
    error: '#EF4444',
    warning: '#F59E0B',
    info: '#3B82F6',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
};

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
  }

  #root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
`;

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: ${props => props.theme.colors.background};
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: ${props => props.sidebarOpen ? '280px' : '0'};
  transition: margin-left 0.3s ease;

  @media (max-width: 768px) {
    margin-left: 0;
  }
`;

const ContentArea = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.xl};
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;

  @media (max-width: 768px) {
    padding: ${props => props.theme.spacing.md};
  }
`;

const TabContainer = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.md};
  overflow: hidden;
`;

const TabHeader = styled.div`
  display: flex;
  border-bottom: 1px solid ${props => props.theme.colors.border};
  background: ${props => props.theme.colors.surface};
`;

const TabButton = styled.button`
  flex: 1;
  padding: ${props => props.theme.spacing.lg} ${props => props.theme.spacing.xl};
  background: ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? 'white' : props.theme.colors.text};
  border: none;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${props => props.theme.spacing.sm};

  &:hover {
    background: ${props => props.active ? props.theme.colors.primaryDark : props.theme.colors.background};
  }

  &:focus {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: -2px;
  }
`;

const TabContent = styled.div`
  padding: ${props => props.theme.spacing.xl};
  min-height: 600px;

  @media (max-width: 768px) {
    padding: ${props => props.theme.spacing.lg};
  }
`;

function App() {
  const [activeTab, setActiveTab] = useState('qa');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isHealthy, isLoading } = useAPIHealth();

  const tabs = [
    { id: 'qa', label: 'Ask Reviews', icon: '🔍' },
    { id: 'recommendations', label: 'Recommendations', icon: '🎯' },
  ];

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isHealthy) {
    return (
      <ErrorBoundary>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <h1 style={{ color: '#EF4444', marginBottom: '1rem' }}>
            🚫 API Connection Error
          </h1>
          <p style={{ marginBottom: '2rem', color: '#64748B' }}>
            The FastAPI backend is not running. Please start it first:
          </p>
          <div style={{
            background: '#F1F5F9',
            padding: '1rem',
            borderRadius: '0.5rem',
            fontFamily: 'monospace',
            textAlign: 'left'
          }}>
            <div>python api/main.py</div>
            <div style={{ color: '#64748B', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              # API will be available at http://localhost:8000
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Sidebar
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            isHealthy={isHealthy}
          />

          <MainContent sidebarOpen={sidebarOpen}>
            <Header
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
              isHealthy={isHealthy}
            />

            <ContentArea>
              <TabContainer>
                <TabHeader>
                  {tabs.map(tab => (
                    <TabButton
                      key={tab.id}
                      active={activeTab === tab.id}
                      onClick={() => setActiveTab(tab.id)}
                    >
                      <span>{tab.icon}</span>
                      <span>{tab.label}</span>
                    </TabButton>
                  ))}
                </TabHeader>

                <TabContent>
                  {activeTab === 'qa' && <QATab />}
                  {activeTab === 'recommendations' && <RecommendationsTab />}
                </TabContent>
              </TabContainer>
            </ContentArea>
          </MainContent>
        </AppContainer>
      </Router>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1E293B',
            color: '#F8FAFC',
            borderRadius: '0.5rem',
          },
        }}
      />
    </ThemeProvider>
  );
}

export default App;

import React from 'react';
import styled from 'styled-components';
import { Menu, Wifi, WifiOff } from 'lucide-react';

const HeaderContainer = styled.header`
  background: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: ${props => props.theme.spacing.lg} ${props => props.theme.spacing.xl};
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: ${props => props.theme.shadows.sm};
  position: sticky;
  top: 0;
  z-index: 100;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};
`;

const MenuButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.primary};
    color: white;
    border-color: ${props => props.theme.colors.primary};
  }

  @media (min-width: 769px) {
    display: none;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const LogoIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.primaryDark});
  border-radius: ${props => props.theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  font-weight: bold;
`;

const LogoText = styled.div`
  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: ${props => props.theme.colors.text};
    margin: 0;
  }

  p {
    font-size: 0.875rem;
    color: ${props => props.theme.colors.textSecondary};
    margin: 0;
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.isHealthy ? props.theme.colors.success : props.theme.colors.error};
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
`;

const StatusText = styled.span`
  @media (max-width: 640px) {
    display: none;
  }
`;

const Header = ({ onMenuClick, isHealthy }) => {
  return (
    <HeaderContainer>
      <LeftSection>
        <MenuButton onClick={onMenuClick}>
          <Menu size={20} />
        </MenuButton>

        <Logo>
          <LogoIcon>🛍️</LogoIcon>
          <LogoText>
            <h1>Amazon Review Intelligence</h1>
            <p>AI-Powered QA & Recommendations</p>
          </LogoText>
        </Logo>
      </LeftSection>

      <RightSection>
        <StatusIndicator isHealthy={isHealthy}>
          {isHealthy ? <Wifi size={16} /> : <WifiOff size={16} />}
          <StatusText>
            {isHealthy ? 'API Connected' : 'API Disconnected'}
          </StatusText>
        </StatusIndicator>
      </RightSection>
    </HeaderContainer>
  );
};

export default Header;

import React from 'react';
import styled from 'styled-components';
import { X, BarChart3, HelpCircle, Settings, ExternalLink } from 'lucide-react';

const SidebarContainer = styled.aside`
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 280px;
  background: ${props => props.theme.colors.surface};
  border-right: 1px solid ${props => props.theme.colors.border};
  transform: translateX(${props => props.isOpen ? '0' : '-100%'});
  transition: transform 0.3s ease;
  z-index: 200;
  overflow-y: auto;
  box-shadow: ${props => props.isOpen ? props.theme.shadows.lg : 'none'};

  @media (min-width: 769px) {
    transform: translateX(0);
    position: relative;
    box-shadow: none;
  }
`;

const SidebarHeader = styled.div`
  padding: ${props => props.theme.spacing.xl};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const CloseButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
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

const SidebarContent = styled.div`
  padding: ${props => props.theme.spacing.lg};
`;

const Section = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const SectionTitle = styled.h3`
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const MenuItem = styled.button`
  width: 100%;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  background: transparent;
  border: none;
  color: ${props => props.theme.colors.text};
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: ${props => props.theme.spacing.xs};

  &:hover {
    background: ${props => props.theme.colors.background};
  }

  &:focus {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: -2px;
  }
`;

const MenuIcon = styled.div`
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const MenuText = styled.span`
  font-weight: 500;
`;

const StatsContainer = styled.div`
  background: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StatItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.border};

  &:last-child {
    border-bottom: none;
  }
`;

const StatLabel = styled.span`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const StatValue = styled.span`
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const StatusBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  background: ${props => props.isHealthy ? props.theme.colors.success : props.theme.colors.error};
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
`;

const Sidebar = ({ isOpen, onToggle, isHealthy }) => {
  const menuItems = [
    { icon: <BarChart3 size={20} />, label: 'Dashboard', action: () => {} },
    { icon: <HelpCircle size={20} />, label: 'Help & Support', action: () => {} },
    { icon: <Settings size={20} />, label: 'Settings', action: () => {} },
  ];

  const externalLinks = [
    { icon: <ExternalLink size={20} />, label: 'API Documentation', url: 'http://localhost:8000/docs' },
    { icon: <ExternalLink size={20} />, label: 'GitHub Repository', url: '#' },
  ];

  return (
    <SidebarContainer isOpen={isOpen}>
      <SidebarHeader>
        <h2>Menu</h2>
        <CloseButton onClick={onToggle}>
          <X size={20} />
        </CloseButton>
      </SidebarHeader>

      <SidebarContent>
        <Section>
          <SectionTitle>System Status</SectionTitle>
          <StatsContainer>
            <StatItem>
              <StatLabel>API Status</StatLabel>
              <StatusBadge isHealthy={isHealthy}>
                {isHealthy ? '✓' : '✗'}
                {isHealthy ? 'Connected' : 'Disconnected'}
              </StatusBadge>
            </StatItem>
            <StatItem>
              <StatLabel>System</StatLabel>
              <StatValue>Operational</StatValue>
            </StatItem>
            <StatItem>
              <StatLabel>Version</StatLabel>
              <StatValue>v1.0.0</StatValue>
            </StatItem>
          </StatsContainer>
        </Section>

        <Section>
          <SectionTitle>Navigation</SectionTitle>
          {menuItems.map((item, index) => (
            <MenuItem key={index} onClick={item.action}>
              <MenuIcon>{item.icon}</MenuIcon>
              <MenuText>{item.label}</MenuText>
            </MenuItem>
          ))}
        </Section>

        <Section>
          <SectionTitle>External Links</SectionTitle>
          {externalLinks.map((link, index) => (
            <MenuItem key={index} onClick={() => window.open(link.url, '_blank')}>
              <MenuIcon>{link.icon}</MenuIcon>
              <MenuText>{link.label}</MenuText>
            </MenuItem>
          ))}
        </Section>
      </SidebarContent>
    </SidebarContainer>
  );
};

export default Sidebar;

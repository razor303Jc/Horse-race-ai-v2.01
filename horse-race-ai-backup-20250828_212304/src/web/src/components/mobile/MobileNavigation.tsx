import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Badge,
  useTheme,
  useMediaQuery,
  Divider,
  Avatar,
  Chip,
  SwipeableDrawer,
  Fab,
  Zoom,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Collapse,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home,
  TrendingUp,
  Assessment,
  AccountBalance,
  Settings,
  Notifications,
  Person,
  Dashboard,
  SportsSoccer,
  MonetizationOn,
  Analytics,
  Security,
  Help,
  Feedback,
  ExitToApp,
  Add,
  PlayArrow,
  Pause,
  Stop,
  Share,
  Download,
  Bookmark,
  FavoriteBorder,
  ExpandLess,
  ExpandMore,
  Brightness4,
  Brightness7,
  Wifi,
  WifiOff,
  CloudOff,
  CloudDone
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface MobileNavigationProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
    subscription: 'free' | 'premium' | 'professional';
  };
  notifications?: number;
  onThemeToggle?: () => void;
  isDarkMode?: boolean;
}

interface NavigationItem {
  title: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
  children?: NavigationItem[];
  requiresAuth?: boolean;
  subscriptionRequired?: 'premium' | 'professional';
}

export const MobileNavigation: React.FC<MobileNavigationProps> = ({
  user,
  notifications = 0,
  onThemeToggle,
  isDarkMode = false
}) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);
  const [showOfflineAlert, setShowOfflineAlert] = useState(false);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  // Navigation items configuration
  const navigationItems: NavigationItem[] = [
    {
      title: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard'
    },
    {
      title: "Today's Races",
      icon: <SportsSoccer />,
      path: '/races/today',
      badge: 5
    },
    {
      title: 'Betting',
      icon: <MonetizationOn />,
      path: '/betting',
      children: [
        { title: 'Betting Dashboard', icon: <TrendingUp />, path: '/betting/dashboard' },
        { title: 'Live Betting', icon: <PlayArrow />, path: '/betting/live' },
        { title: 'Portfolio', icon: <AccountBalance />, path: '/betting/portfolio' }
      ]
    },
    {
      title: 'Analytics',
      icon: <Analytics />,
      path: '/analytics',
      children: [
        { title: 'Performance', icon: <Assessment />, path: '/analytics/performance' },
        { title: 'Advanced Analytics', icon: <TrendingUp />, path: '/analytics/advanced', subscriptionRequired: 'premium' },
        { title: 'Risk Analysis', icon: <Security />, path: '/analytics/risk', subscriptionRequired: 'professional' }
      ]
    },
    {
      title: 'Profile',
      icon: <Person />,
      path: '/profile',
      children: [
        { title: 'Settings', icon: <Settings />, path: '/profile/settings' },
        { title: 'Subscription', icon: <AccountBalance />, path: '/profile/subscription' },
        { title: 'Security', icon: <Security />, path: '/profile/security' }
      ]
    }
  ];

  // Quick actions for speed dial
  const quickActions = [
    {
      icon: <PlayArrow />,
      name: 'Quick Bet',
      action: () => navigate('/betting/quick')
    },
    {
      icon: <Bookmark />,
      name: 'Favorites',
      action: () => navigate('/favorites')
    },
    {
      icon: <Share />,
      name: 'Share',
      action: () => handleShare()
    },
    {
      icon: <Download />,
      name: 'Offline Mode',
      action: () => toggleOfflineMode()
    }
  ];

  // Online/offline detection
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineAlert(false);
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineAlert(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleSectionToggle = (title: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(title)) {
      newExpanded.delete(title);
    } else {
      newExpanded.add(title);
    }
    setExpandedSections(newExpanded);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setDrawerOpen(false);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Horse Racing AI',
          text: 'Check out this amazing racing prediction platform!',
          url: window.location.href
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback for browsers without Web Share API
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(window.location.href);
        // Show toast notification
      }
    }
  };

  const toggleOfflineMode = () => {
    // Implement offline mode toggle
    console.log('Toggle offline mode');
  };

  const getSubscriptionColor = (subscription: string) => {
    switch (subscription) {
      case 'professional': return 'primary';
      case 'premium': return 'secondary';
      default: return 'default';
    }
  };

  const renderNavigationItem = (item: NavigationItem, depth = 0) => {
    const isActive = location.pathname === item.path;
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedSections.has(item.title);
    const isSubscriptionRestricted = item.subscriptionRequired && 
      user?.subscription !== item.subscriptionRequired && 
      user?.subscription !== 'professional';

    return (
      <React.Fragment key={item.title}>
        <ListItemButton
          onClick={() => {
            if (hasChildren) {
              handleSectionToggle(item.title);
            } else {
              handleNavigation(item.path);
            }
          }}
          selected={isActive}
          disabled={isSubscriptionRestricted}
          sx={{
            pl: 2 + depth * 2,
            backgroundColor: isActive ? theme.palette.action.selected : 'transparent',
            '&.Mui-disabled': {
              opacity: 0.5
            }
          }}
        >
          <ListItemIcon>
            <Badge badgeContent={item.badge} color="error">
              {item.icon}
            </Badge>
          </ListItemIcon>
          <ListItemText 
            primary={item.title}
            secondary={isSubscriptionRestricted ? `${item.subscriptionRequired} required` : undefined}
          />
          {item.subscriptionRequired && (
            <Chip 
              label={item.subscriptionRequired} 
              size="small" 
              color={getSubscriptionColor(item.subscriptionRequired)}
              sx={{ ml: 1 }}
            />
          )}
          {hasChildren && (isExpanded ? <ExpandLess /> : <ExpandMore />)}
        </ListItemButton>
        
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderNavigationItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawerContent = (
    <Box sx={{ width: 280, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* User Profile Section */}
      {user && (
        <Box sx={{ p: 2, backgroundColor: theme.palette.primary.main, color: 'white' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Avatar src={user.avatar} sx={{ mr: 2 }}>
              {user.name.charAt(0)}
            </Avatar>
            <Box>
              <Typography variant="h6" noWrap>
                {user.name}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }} noWrap>
                {user.email}
              </Typography>
            </Box>
          </Box>
          <Chip 
            label={user.subscription.toUpperCase()} 
            size="small" 
            color={getSubscriptionColor(user.subscription)}
            sx={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
          />
        </Box>
      )}

      {/* Network Status */}
      <Box sx={{ p: 1 }}>
        <Alert 
          severity={isOnline ? "success" : "warning"} 
          icon={isOnline ? <CloudDone /> : <CloudOff />}
          sx={{ fontSize: '0.75rem' }}
        >
          {isOnline ? "Online" : "Offline Mode"}
        </Alert>
      </Box>

      {/* Navigation Items */}
      <List sx={{ flex: 1, overflow: 'auto' }}>
        {navigationItems.map(item => renderNavigationItem(item))}
      </List>

      <Divider />

      {/* Settings and Actions */}
      <List>
        <ListItemButton onClick={onThemeToggle}>
          <ListItemIcon>
            {isDarkMode ? <Brightness7 /> : <Brightness4 />}
          </ListItemIcon>
          <ListItemText primary={isDarkMode ? "Light Mode" : "Dark Mode"} />
        </ListItemButton>
        
        <ListItemButton onClick={() => navigate('/help')}>
          <ListItemIcon><Help /></ListItemIcon>
          <ListItemText primary="Help & Support" />
        </ListItemButton>
        
        <ListItemButton onClick={() => navigate('/feedback')}>
          <ListItemIcon><Feedback /></ListItemIcon>
          <ListItemText primary="Feedback" />
        </ListItemButton>
        
        {user && (
          <ListItemButton onClick={() => navigate('/logout')}>
            <ListItemIcon><ExitToApp /></ListItemIcon>
            <ListItemText primary="Sign Out" />
          </ListItemButton>
        )}
      </List>
    </Box>
  );

  return (
    <>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Racing AI
          </Typography>

          {/* Network Status Icon */}
          <IconButton color="inherit">
            {isOnline ? <Wifi /> : <WifiOff />}
          </IconButton>

          {/* Notifications */}
          <IconButton color="inherit">
            <Badge badgeContent={notifications} color="error">
              <Notifications />
            </Badge>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <SwipeableDrawer
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        onOpen={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: 280,
          },
        }}
      >
        {drawerContent}
      </SwipeableDrawer>

      {/* Quick Actions Speed Dial */}
      {isMobile && (
        <SpeedDial
          ariaLabel="Quick Actions"
          sx={{ 
            position: 'fixed', 
            bottom: 80, 
            right: 16,
            '& .MuiFab-primary': {
              backgroundColor: theme.palette.primary.main
            }
          }}
          icon={<SpeedDialIcon />}
          onClose={() => setQuickActionsOpen(false)}
          onOpen={() => setQuickActionsOpen(true)}
          open={quickActionsOpen}
        >
          {quickActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={() => {
                action.action();
                setQuickActionsOpen(false);
              }}
            />
          ))}
        </SpeedDial>
      )}

      {/* Offline Alert */}
      <Snackbar
        open={showOfflineAlert}
        autoHideDuration={6000}
        onClose={() => setShowOfflineAlert(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowOfflineAlert(false)} 
          severity="warning"
          icon={<WifiOff />}
        >
          You are currently offline. Some features may be limited.
        </Alert>
      </Snackbar>

      {/* Toolbar Spacer */}
      <Toolbar />
    </>
  );
};

export default MobileNavigation;

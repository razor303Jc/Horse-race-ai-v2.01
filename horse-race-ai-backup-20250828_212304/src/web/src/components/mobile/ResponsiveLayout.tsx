import React, { useState, useEffect, ReactNode } from 'react';
import {
  Box,
  useTheme,
  useMediaQuery,
  Container,
  Fab,
  Zoom,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
  SwipeableDrawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  alpha,
  Backdrop,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  Home,
  TrendingUp,
  Assessment,
  AccountBalance,
  Settings,
  Menu as MenuIcon,
  ArrowUpward,
  Share,
  Bookmark,
  Refresh,
  Download,
  Notifications,
  Search,
  Add,
  Remove
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

interface ResponsiveLayoutProps {
  children: ReactNode;
  showBottomNav?: boolean;
  showSpeedDial?: boolean;
  showScrollToTop?: boolean;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  disablePadding?: boolean;
  backgroundColor?: string;
}

interface NavigationItem {
  label: string;
  value: string;
  icon: ReactNode;
  path: string;
}

const BOTTOM_NAV_HEIGHT = 56;
const APP_BAR_HEIGHT = 64;

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  showBottomNav = true,
  showSpeedDial = true,
  showScrollToTop = true,
  maxWidth = 'lg',
  disablePadding = false,
  backgroundColor
}) => {
  const [scrollY, setScrollY] = useState(0);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const location = useLocation();
  const navigate = useNavigate();

  // Bottom navigation items
  const bottomNavItems: NavigationItem[] = [
    { label: 'Home', value: 'home', icon: <Home />, path: '/dashboard' },
    { label: 'Races', value: 'races', icon: <TrendingUp />, path: '/races' },
    { label: 'Betting', value: 'betting', icon: <AccountBalance />, path: '/betting' },
    { label: 'Analytics', value: 'analytics', icon: <Assessment />, path: '/analytics' },
    { label: 'More', value: 'more', icon: <MenuIcon />, path: '/menu' }
  ];

  // Speed dial actions
  const speedDialActions = [
    {
      icon: <Share />,
      name: 'Share',
      action: () => handleShare()
    },
    {
      icon: <Bookmark />,
      name: 'Bookmark',
      action: () => handleBookmark()
    },
    {
      icon: <Refresh />,
      name: 'Refresh',
      action: () => window.location.reload()
    },
    {
      icon: <Download />,
      name: 'Offline',
      action: () => handleOfflineMode()
    }
  ];

  // Scroll handling
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      setScrollY(currentScrollY);
      setShowScrollTop(currentScrollY > 300);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Update bottom nav based on current route
  useEffect(() => {
    const currentPath = location.pathname;
    const currentIndex = bottomNavItems.findIndex(item => 
      currentPath.startsWith(item.path) || currentPath === item.path
    );
    if (currentIndex !== -1) {
      setBottomNavValue(currentIndex);
    }
  }, [location.pathname, bottomNavItems]);

  const handleBottomNavChange = (event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    navigate(bottomNavItems[newValue].path);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Horse Racing AI',
          text: 'Check out this racing prediction!',
          url: window.location.href
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    }
    setSpeedDialOpen(false);
  };

  const handleBookmark = () => {
    // Implement bookmark functionality
    setSpeedDialOpen(false);
  };

  const handleOfflineMode = () => {
    // Implement offline mode toggle
    setSpeedDialOpen(false);
  };

  // Dynamic spacing based on screen size and nav elements
  const getContentSpacing = () => {
    let paddingTop = 0;
    let paddingBottom = 0;

    if (isMobile && showBottomNav) {
      paddingBottom = BOTTOM_NAV_HEIGHT + 16;
    }

    return {
      paddingTop: disablePadding ? 0 : paddingTop + 16,
      paddingBottom: disablePadding ? 0 : paddingBottom,
      paddingLeft: disablePadding ? 0 : 16,
      paddingRight: disablePadding ? 0 : 16,
      minHeight: `calc(100vh - ${paddingTop + paddingBottom}px)`
    };
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: backgroundColor || theme.palette.background.default,
        position: 'relative'
      }}
    >
      {/* Main Content */}
      <Container
        maxWidth={maxWidth}
        sx={{
          ...getContentSpacing(),
          transition: theme.transitions.create(['padding'], {
            duration: theme.transitions.duration.standard,
          })
        }}
      >
        {children}
      </Container>

      {/* Bottom Navigation for Mobile */}
      {isMobile && showBottomNav && (
        <Paper
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: theme.zIndex.appBar,
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: alpha(theme.palette.background.paper, 0.95),
            backdropFilter: 'blur(8px)'
          }}
          elevation={3}
        >
          <BottomNavigation
            value={bottomNavValue}
            onChange={handleBottomNavChange}
            sx={{
              height: BOTTOM_NAV_HEIGHT,
              '& .MuiBottomNavigationAction-root': {
                minWidth: 'auto',
                padding: '6px 12px 8px',
                '&.Mui-selected': {
                  color: theme.palette.primary.main
                }
              }
            }}
          >
            {bottomNavItems.map((item, index) => (
              <BottomNavigationAction
                key={item.value}
                label={item.label}
                value={index}
                icon={item.icon}
                sx={{
                  fontSize: '0.75rem',
                  '& .MuiBottomNavigationAction-label': {
                    fontSize: '0.7rem',
                    marginTop: '2px'
                  }
                }}
              />
            ))}
          </BottomNavigation>
        </Paper>
      )}

      {/* Scroll to Top FAB */}
      {showScrollToTop && (
        <Zoom in={showScrollTop}>
          <Fab
            size="small"
            aria-label="scroll to top"
            onClick={scrollToTop}
            sx={{
              position: 'fixed',
              bottom: isMobile && showBottomNav ? BOTTOM_NAV_HEIGHT + 16 : 16,
              right: 16,
              zIndex: theme.zIndex.fab,
              backgroundColor: alpha(theme.palette.primary.main, 0.9),
              '&:hover': {
                backgroundColor: theme.palette.primary.main
              }
            }}
          >
            <ArrowUpward />
          </Fab>
        </Zoom>
      )}

      {/* Speed Dial for Quick Actions */}
      {isMobile && showSpeedDial && (
        <SpeedDial
          ariaLabel="Quick Actions"
          sx={{
            position: 'fixed',
            bottom: showBottomNav ? BOTTOM_NAV_HEIGHT + 80 : 80,
            right: 16,
            zIndex: theme.zIndex.speedDial,
            '& .MuiFab-primary': {
              backgroundColor: alpha(theme.palette.secondary.main, 0.9),
              '&:hover': {
                backgroundColor: theme.palette.secondary.main
              }
            }
          }}
          icon={<SpeedDialIcon />}
          onClose={() => setSpeedDialOpen(false)}
          onOpen={() => setSpeedDialOpen(true)}
          open={speedDialOpen}
          direction="up"
        >
          {speedDialActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={action.action}
              sx={{
                '& .MuiSpeedDialAction-fab': {
                  backgroundColor: alpha(theme.palette.background.paper, 0.9),
                  '&:hover': {
                    backgroundColor: theme.palette.background.paper
                  }
                }
              }}
            />
          ))}
        </SpeedDial>
      )}

      {/* Backdrop for Speed Dial */}
      <Backdrop
        open={speedDialOpen}
        onClick={() => setSpeedDialOpen(false)}
        sx={{
          zIndex: theme.zIndex.speedDial - 1,
          backgroundColor: alpha(theme.palette.common.black, 0.2)
        }}
      />
    </Box>
  );
};

// Mobile-optimized container component
export const MobileContainer: React.FC<{
  children: ReactNode;
  padding?: boolean;
  fullHeight?: boolean;
  backgroundColor?: string;
}> = ({
  children,
  padding = true,
  fullHeight = false,
  backgroundColor
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: isMobile ? '100%' : 'sm',
        margin: '0 auto',
        padding: padding ? (isMobile ? 1 : 2) : 0,
        minHeight: fullHeight ? '100vh' : 'auto',
        backgroundColor: backgroundColor || 'transparent'
      }}
    >
      {children}
    </Box>
  );
};

// Touch-optimized component for mobile interactions
export const TouchOptimized: React.FC<{
  children: ReactNode;
  onTap?: () => void;
  onLongPress?: () => void;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
}> = ({
  children,
  onTap,
  onLongPress,
  onSwipeLeft,
  onSwipeRight,
  className
}) => {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number; time: number } | null>(null);
  const [longPressTimer, setLongPressTimer] = useState<NodeJS.Timeout | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    });

    // Start long press timer
    if (onLongPress) {
      const timer = setTimeout(() => {
        onLongPress();
        setLongPressTimer(null);
      }, 500);
      setLongPressTimer(timer);
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }

    if (!touchStart) return;

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.x;
    const deltaY = touch.clientY - touchStart.y;
    const deltaTime = Date.now() - touchStart.time;

    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    // Tap detection
    if (distance < 10 && deltaTime < 300 && onTap) {
      onTap();
    }
    // Swipe detection
    else if (distance > 50 && deltaTime < 300) {
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        // Horizontal swipe
        if (deltaX > 0 && onSwipeRight) {
          onSwipeRight();
        } else if (deltaX < 0 && onSwipeLeft) {
          onSwipeLeft();
        }
      }
    }

    setTouchStart(null);
  };

  const handleTouchMove = () => {
    // Cancel long press on move
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
  };

  return (
    <Box
      className={className}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onTouchMove={handleTouchMove}
      sx={{
        userSelect: 'none',
        WebkitTouchCallout: 'none',
        WebkitUserSelect: 'none',
        touchAction: 'manipulation'
      }}
    >
      {children}
    </Box>
  );
};

export default ResponsiveLayout;

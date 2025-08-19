import { createTheme, ThemeOptions } from '@mui/material/styles';
import { PaletteMode } from '@mui/material';

declare module '@mui/material/styles' {
  interface BreakpointOverrides {
    xs: true;
    sm: true;
    md: true;
    lg: true;
    xl: true;
    mobile: true;
    tablet: true;
    laptop: true;
    desktop: true;
  }

  interface Palette {
    gradient: {
      primary: string;
      secondary: string;
      success: string;
      warning: string;
      error: string;
    };
  }

  interface PaletteOptions {
    gradient?: {
      primary?: string;
      secondary?: string;
      success?: string;
      warning?: string;
      error?: string;
    };
  }
}

export const createMobileTheme = (mode: PaletteMode) => {
  const isDark = mode === 'dark';

  const themeOptions: ThemeOptions = {
    palette: {
      mode,
      primary: {
        main: '#1976d2',
        light: '#42a5f5',
        dark: '#1565c0',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#dc004e',
        light: '#ff5983',
        dark: '#9a0036',
        contrastText: '#ffffff',
      },
      success: {
        main: '#2e7d32',
        light: '#4caf50',
        dark: '#1b5e20',
      },
      warning: {
        main: '#ed6c02',
        light: '#ff9800',
        dark: '#e65100',
      },
      error: {
        main: '#d32f2f',
        light: '#ef5350',
        dark: '#c62828',
      },
      background: {
        default: isDark ? '#0a0a0a' : '#f8f9fa',
        paper: isDark ? '#1e1e1e' : '#ffffff',
      },
      text: {
        primary: isDark ? '#ffffff' : '#2c2c2c',
        secondary: isDark ? '#b3b3b3' : '#6c757d',
      },
      gradient: {
        primary: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
        secondary: 'linear-gradient(135deg, #dc004e 0%, #ff5983 100%)',
        success: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
        warning: 'linear-gradient(135deg, #ed6c02 0%, #ff9800 100%)',
        error: 'linear-gradient(135deg, #d32f2f 0%, #ef5350 100%)',
      },
    },
    breakpoints: {
      values: {
        xs: 0,
        mobile: 480,
        sm: 600,
        tablet: 768,
        md: 900,
        laptop: 1024,
        lg: 1200,
        desktop: 1440,
        xl: 1536,
      },
    },
    typography: {
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
      h1: {
        fontSize: '2rem',
        fontWeight: 700,
        lineHeight: 1.2,
        '@media (max-width: 600px)': {
          fontSize: '1.75rem',
        },
      },
      h2: {
        fontSize: '1.75rem',
        fontWeight: 600,
        lineHeight: 1.3,
        '@media (max-width: 600px)': {
          fontSize: '1.5rem',
        },
      },
      h3: {
        fontSize: '1.5rem',
        fontWeight: 600,
        lineHeight: 1.3,
        '@media (max-width: 600px)': {
          fontSize: '1.25rem',
        },
      },
      h4: {
        fontSize: '1.25rem',
        fontWeight: 600,
        lineHeight: 1.4,
        '@media (max-width: 600px)': {
          fontSize: '1.125rem',
        },
      },
      h5: {
        fontSize: '1.125rem',
        fontWeight: 600,
        lineHeight: 1.4,
        '@media (max-width: 600px)': {
          fontSize: '1rem',
        },
      },
      h6: {
        fontSize: '1rem',
        fontWeight: 600,
        lineHeight: 1.4,
        '@media (max-width: 600px)': {
          fontSize: '0.9rem',
        },
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.5,
        '@media (max-width: 600px)': {
          fontSize: '0.9rem',
        },
      },
      body2: {
        fontSize: '0.875rem',
        lineHeight: 1.4,
        '@media (max-width: 600px)': {
          fontSize: '0.8rem',
        },
      },
      button: {
        textTransform: 'none',
        fontWeight: 600,
        fontSize: '0.875rem',
      },
    },
    shape: {
      borderRadius: 12,
    },
    spacing: 8,
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            scrollbarWidth: 'thin',
            scrollbarColor: isDark ? '#6b6b6b #2b2b2b' : '#c1c1c1 #f1f1f1',
            '&::-webkit-scrollbar': {
              width: '6px',
            },
            '&::-webkit-scrollbar-track': {
              background: isDark ? '#2b2b2b' : '#f1f1f1',
            },
            '&::-webkit-scrollbar-thumb': {
              background: isDark ? '#6b6b6b' : '#c1c1c1',
              borderRadius: '3px',
            },
            // Prevent text selection on mobile for better UX
            '@media (max-width: 768px)': {
              WebkitTouchCallout: 'none',
              WebkitUserSelect: 'none',
              userSelect: 'none',
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            padding: '8px 16px',
            fontSize: '0.875rem',
            minHeight: 44, // Minimum touch target size
            '@media (max-width: 600px)': {
              minHeight: 48, // Larger touch targets on mobile
              fontSize: '0.9rem',
            },
          },
          contained: {
            boxShadow: 'none',
            '&:hover': {
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            },
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            padding: 8,
            '@media (max-width: 600px)': {
              padding: 12, // Larger touch targets on mobile
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: isDark 
              ? '0 2px 8px rgba(0,0,0,0.4)' 
              : '0 2px 8px rgba(0,0,0,0.1)',
            transition: 'box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out',
            '&:hover': {
              boxShadow: isDark 
                ? '0 4px 16px rgba(0,0,0,0.6)' 
                : '0 4px 16px rgba(0,0,0,0.15)',
              transform: 'translateY(-1px)',
            },
            '@media (max-width: 600px)': {
              borderRadius: 8,
              margin: '0 -4px', // Extend to screen edges on mobile
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: 'none',
            borderBottom: `1px solid ${isDark ? '#333' : '#e0e0e0'}`,
            backgroundColor: isDark ? '#1e1e1e' : '#ffffff',
            color: isDark ? '#ffffff' : '#2c2c2c',
          },
        },
      },
      MuiToolbar: {
        styleOverrides: {
          root: {
            '@media (max-width: 600px)': {
              paddingLeft: 8,
              paddingRight: 8,
            },
          },
        },
      },
      MuiBottomNavigation: {
        styleOverrides: {
          root: {
            height: 56,
            backgroundColor: isDark ? '#1e1e1e' : '#ffffff',
            borderTop: `1px solid ${isDark ? '#333' : '#e0e0e0'}`,
          },
        },
      },
      MuiBottomNavigationAction: {
        styleOverrides: {
          root: {
            minWidth: 'auto',
            padding: '6px 12px 8px',
            '&.Mui-selected': {
              color: '#1976d2',
            },
            '@media (max-width: 480px)': {
              fontSize: '0.7rem',
              padding: '4px 8px 6px',
            },
          },
        },
      },
      MuiFab: {
        styleOverrides: {
          root: {
            boxShadow: isDark 
              ? '0 4px 12px rgba(0,0,0,0.6)' 
              : '0 4px 12px rgba(0,0,0,0.15)',
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          root: {
            '@media (max-width: 600px)': {
              '& .MuiDialog-paper': {
                margin: 8,
                width: 'calc(100% - 16px)',
                maxHeight: 'calc(100% - 16px)',
              },
            },
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: isDark ? '#1e1e1e' : '#ffffff',
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 6,
            fontSize: '0.75rem',
            height: 24,
            '@media (max-width: 600px)': {
              fontSize: '0.7rem',
              height: 28,
            },
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: 4,
            backgroundColor: isDark ? '#333' : '#e0e0e0',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
              '@media (max-width: 600px)': {
                fontSize: '16px', // Prevent zoom on iOS
              },
            },
          },
        },
      },
      MuiInputBase: {
        styleOverrides: {
          root: {
            '@media (max-width: 600px)': {
              fontSize: '16px', // Prevent zoom on iOS
            },
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          root: {
            minHeight: 48,
          },
          flexContainer: {
            '@media (max-width: 600px)': {
              justifyContent: 'space-around',
            },
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            minHeight: 48,
            fontSize: '0.875rem',
            textTransform: 'none',
            '@media (max-width: 600px)': {
              fontSize: '0.8rem',
              minWidth: 'auto',
              padding: '6px 8px',
            },
          },
        },
      },
    },
  };

  return createTheme(themeOptions);
};

// Responsive utilities
export const getResponsiveValue = (
  xs: any,
  sm?: any,
  md?: any,
  lg?: any,
  xl?: any
) => ({
  xs,
  sm: sm || xs,
  md: md || sm || xs,
  lg: lg || md || sm || xs,
  xl: xl || lg || md || sm || xs,
});

// Mobile breakpoint helpers
export const mobileBreakpoints = {
  isMobile: '(max-width: 767px)',
  isTablet: '(min-width: 768px) and (max-width: 1023px)',
  isDesktop: '(min-width: 1024px)',
  isTouchDevice: '(hover: none) and (pointer: coarse)',
  isRetina: '(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)',
};

// Animation variants for mobile
export const mobileAnimations = {
  slideInFromBottom: {
    initial: { y: '100%', opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: '100%', opacity: 0 },
    transition: { type: 'spring', damping: 25, stiffness: 300 },
  },
  slideInFromRight: {
    initial: { x: '100%', opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: '100%', opacity: 0 },
    transition: { type: 'spring', damping: 25, stiffness: 300 },
  },
  fadeIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: 0.2 },
  },
  scaleIn: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0, opacity: 0 },
    transition: { type: 'spring', damping: 20, stiffness: 300 },
  },
};

export default createMobileTheme;

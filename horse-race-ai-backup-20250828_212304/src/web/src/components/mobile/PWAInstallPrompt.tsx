import React, { useEffect, useState } from 'react';
import {
  Alert,
  Snackbar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  IconButton,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  CloudDownload,
  CloudDone,
  CloudOff,
  Refresh,
  Close,
  GetApp,
  Update,
  Wifi,
  WifiOff
} from '@mui/icons-material';

interface PWAInstallPromptProps {
  onInstallPrompt?: (deferredPrompt: any) => void;
}

export const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({ onInstallPrompt }) => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [swUpdate, setSwUpdate] = useState<ServiceWorkerRegistration | null>(null);
  const [showUpdatePrompt, setShowUpdatePrompt] = useState(false);
  const [cacheProgress, setCacheProgress] = useState(0);
  const [cachingComplete, setCachingComplete] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    const checkInstalled = () => {
      if (window.matchMedia('(display-mode: standalone)').matches || 
          (window.navigator as any).standalone) {
        setIsInstalled(true);
      }
    };

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
      onInstallPrompt?.(e);
    };

    // Listen for app installed event
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowInstallPrompt(false);
      setDeferredPrompt(null);
    };

    // Online/offline detection
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Register service worker
    const registerServiceWorker = async () => {
      if ('serviceWorker' in navigator) {
        try {
          const registration = await navigator.serviceWorker.register('/sw.js', {
            scope: '/'
          });

          console.log('Service Worker registered:', registration);

          // Listen for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  setSwUpdate(registration);
                  setShowUpdatePrompt(true);
                }
              });
            }
          });

          // Check for existing update
          if (registration.waiting) {
            setSwUpdate(registration);
            setShowUpdatePrompt(true);
          }

          // Listen for cache progress messages
          navigator.serviceWorker.addEventListener('message', (event) => {
            if (event.data && event.data.type === 'CACHE_PROGRESS') {
              setCacheProgress(event.data.progress);
              if (event.data.progress === 100) {
                setCachingComplete(true);
                setTimeout(() => setCachingComplete(false), 3000);
              }
            }
          });

        } catch (error) {
          console.error('Service Worker registration failed:', error);
        }
      }
    };

    checkInstalled();
    registerServiceWorker();

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [onInstallPrompt]);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    }
  };

  const handleUpdateClick = () => {
    if (swUpdate?.waiting) {
      swUpdate.waiting.postMessage({ type: 'SKIP_WAITING' });
      setShowUpdatePrompt(false);
      window.location.reload();
    }
  };

  const handleDismissInstall = () => {
    setShowInstallPrompt(false);
    // Hide for 24 hours
    localStorage.setItem('pwa_install_dismissed', Date.now().toString());
  };

  // Check if install prompt was recently dismissed
  useEffect(() => {
    const dismissed = localStorage.getItem('pwa_install_dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      const hoursSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60);
      if (hoursSinceDismissed < 24) {
        setShowInstallPrompt(false);
      }
    }
  }, []);

  return (
    <>
      {/* Install Prompt Dialog */}
      <Dialog open={showInstallPrompt && !isInstalled} onClose={handleDismissInstall}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <GetApp />
            Install Racing AI
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Install Racing AI as a Progressive Web App for the best mobile experience:
          </Typography>
          <Box component="ul" sx={{ mt: 2, pl: 2 }}>
            <li>Faster loading times</li>
            <li>Offline functionality</li>
            <li>Push notifications for race alerts</li>
            <li>Full-screen app experience</li>
            <li>Quick access from home screen</li>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDismissInstall}>
            Not Now
          </Button>
          <Button variant="contained" onClick={handleInstallClick} startIcon={<GetApp />}>
            Install App
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Prompt */}
      <Snackbar
        open={showUpdatePrompt}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{ bottom: 80 }}
      >
        <Alert
          severity="info"
          action={
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                color="inherit"
                size="small"
                onClick={handleUpdateClick}
                startIcon={<Update />}
              >
                Update
              </Button>
              <IconButton
                size="small"
                color="inherit"
                onClick={() => setShowUpdatePrompt(false)}
              >
                <Close />
              </IconButton>
            </Box>
          }
        >
          A new version is available!
        </Alert>
      </Snackbar>

      {/* Online/Offline Status */}
      <Snackbar
        open={!isOnline}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="warning" icon={<WifiOff />}>
          You are currently offline. Some features may be limited.
        </Alert>
      </Snackbar>

      {/* Cache Progress */}
      {cacheProgress > 0 && cacheProgress < 100 && (
        <Snackbar
          open={true}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="info" icon={<CloudDownload />}>
            <Typography variant="body2" gutterBottom>
              Caching app for offline use...
            </Typography>
            <LinearProgress variant="determinate" value={cacheProgress} />
          </Alert>
        </Snackbar>
      )}

      {/* Cache Complete */}
      <Snackbar
        open={cachingComplete}
        autoHideDuration={3000}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" icon={<CloudDone />}>
          App is now available offline!
        </Alert>
      </Snackbar>

      {/* PWA Status Indicator */}
      {isInstalled && (
        <Chip
          icon={isOnline ? <Wifi /> : <WifiOff />}
          label={isOnline ? "Online" : "Offline"}
          size="small"
          color={isOnline ? "success" : "warning"}
          sx={{
            position: 'fixed',
            top: 8,
            right: 8,
            zIndex: 1300
          }}
        />
      )}
    </>
  );
};

// Hook for PWA functionality
export const usePWA = () => {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
    };

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const installApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      setDeferredPrompt(null);
      setIsInstallable(false);
      return outcome === 'accepted';
    }
    return false;
  };

  const shareContent = async (data: ShareData) => {
    if (navigator.share) {
      try {
        await navigator.share(data);
        return true;
      } catch (error) {
        console.error('Error sharing:', error);
        return false;
      }
    }
    
    // Fallback to clipboard
    if (navigator.clipboard && data.url) {
      try {
        await navigator.clipboard.writeText(data.url);
        return true;
      } catch (error) {
        console.error('Error copying to clipboard:', error);
        return false;
      }
    }
    
    return false;
  };

  return {
    isInstallable,
    isInstalled,
    isOnline,
    installApp,
    shareContent
  };
};

export default PWAInstallPrompt;

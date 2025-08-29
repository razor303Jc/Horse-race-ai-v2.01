/**
 * Content Security Policy utilities
 * Provides environment-specific CSP configurations for development and production
 */

export const getCSPHeader = (isDevelopment: boolean = process.env.NODE_ENV === 'development'): string => {
  const basePolicy = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'connect-src': ["'self'", 'ws:', 'wss:', 'http:', 'https:'],
    'img-src': ["'self'", 'data:', 'https:'],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  };

  // In development, we need to allow eval for Vite's HMR
  if (isDevelopment) {
    basePolicy['script-src'].push("'unsafe-eval'", "'unsafe-inline'");
  } else {
    // Production configuration: stricter security
    // Remove 'unsafe-eval' and limit 'unsafe-inline' usage
    basePolicy['script-src'].push('https://cdn.jsdelivr.net'); // Allow CDN if needed
    basePolicy['style-src'] = ["'self'", 'https://fonts.googleapis.com']; // Remove unsafe-inline in production
  }

  // Convert policy object to CSP string
  return Object.entries(basePolicy)
    .map(([directive, sources]) => 
      sources.length > 0 ? `${directive} ${sources.join(' ')}` : directive
    )
    .join('; ');
};

export const applyCSP = (): void => {
  const cspHeader = getCSPHeader();
  
  // Create or update CSP meta tag
  let cspMeta = document.querySelector('meta[http-equiv="Content-Security-Policy"]') as HTMLMetaElement;
  
  if (!cspMeta) {
    cspMeta = document.createElement('meta');
    cspMeta.setAttribute('http-equiv', 'Content-Security-Policy');
    document.head.appendChild(cspMeta);
  }
  
  cspMeta.setAttribute('content', cspHeader);
};

// Apply CSP on module load
if (typeof window !== 'undefined') {
  applyCSP();
}

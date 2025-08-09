module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/family-feed',
        'http://localhost:3000/feed/test-pregnancy-id'
      ],
      startServerCommand: 'npm run start',
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox --headless --disable-gpu',
        preset: 'desktop',
        onlyAudits: [
          'first-contentful-paint',
          'largest-contentful-paint',
          'first-input-delay',
          'cumulative-layout-shift',
          'speed-index',
          'interactive',
          'uses-webp-images',
          'uses-optimized-images',
          'uses-text-compression',
          'uses-rel-preconnect',
          'font-display',
          'unused-javascript',
          'unused-css-rules',
          'modern-image-formats',
          'efficient-animated-content',
          'preload-lcp-image',
          'total-byte-weight',
          'dom-size',
          'bootup-time',
          'mainthread-work-breakdown',
          'third-party-summary'
        ]
      }
    },
    assert: {
      assertions: {
        // Performance budget for pregnancy app
        'categories:performance': ['error', { minScore: 0.9 }], // 90+ performance score
        'categories:accessibility': ['error', { minScore: 0.95 }], // 95+ accessibility score
        'categories:best-practices': ['error', { minScore: 0.9 }], // 90+ best practices
        'categories:seo': ['error', { minScore: 0.9 }], // 90+ SEO score
        
        // Core Web Vitals - Pregnancy-focused targets
        'audits:first-contentful-paint': ['error', { maxNumericValue: 1500 }], // 1.5s max
        'audits:largest-contentful-paint': ['error', { maxNumericValue: 2500 }], // 2.5s max
        'audits:cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }], // 0.1 max
        'audits:interactive': ['error', { maxNumericValue: 3500 }], // 3.5s max
        'audits:speed-index': ['error', { maxNumericValue: 3000 }], // 3s max
        
        // Resource optimization
        'audits:total-byte-weight': ['warn', { maxNumericValue: 2000000 }], // 2MB max
        'audits:unused-javascript': ['warn', { maxNumericValue: 100000 }], // 100KB max unused
        'audits:unused-css-rules': ['warn', { maxNumericValue: 50000 }], // 50KB max unused
        'audits:dom-size': ['warn', { maxNumericValue: 1500 }], // 1500 DOM nodes max
        
        // Image optimization - critical for pregnancy photos
        'audits:uses-webp-images': 'error',
        'audits:uses-optimized-images': 'error',
        'audits:modern-image-formats': 'error',
        
        // Network efficiency
        'audits:uses-text-compression': 'error',
        'audits:uses-rel-preconnect': 'error',
        
        // Font optimization
        'audits:font-display': 'error',
        
        // JavaScript performance
        'audits:bootup-time': ['warn', { maxNumericValue: 3000 }], // 3s max
        'audits:mainthread-work-breakdown': ['warn', { maxNumericValue: 3000 }] // 3s max
      }
    },
    upload: {
      target: 'temporary-public-storage'
    },
    server: {
      port: 9001,
      storage: './lighthouse-ci-data'
    }
  }
}
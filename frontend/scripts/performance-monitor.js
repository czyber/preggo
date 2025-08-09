#!/usr/bin/env node

/**
 * Performance monitoring script for Preggo app
 * Continuously monitors performance metrics and alerts on budget violations
 */

const lighthouse = require('lighthouse')
const chromeLauncher = require('chrome-launcher')
const fs = require('fs').promises
const path = require('path')

// Performance budgets specific to pregnancy app
const PERFORMANCE_BUDGETS = {
  // Core Web Vitals
  firstContentfulPaint: 1500, // 1.5s - Critical for pregnancy anxiety
  largestContentfulPaint: 2500, // 2.5s - Feed images load quickly
  firstInputDelay: 100, // 100ms - Responsive interactions
  cumulativeLayoutShift: 0.1, // Stable layout for comfortable viewing
  timeToInteractive: 3500, // 3.5s - App becomes usable quickly
  
  // Resource budgets
  totalTransferSize: 2000000, // 2MB - Mobile-friendly
  unusedJavaScript: 100000, // 100KB - Efficient bundle
  unusedCSS: 50000, // 50KB - Clean CSS
  domSize: 1500, // DOM nodes - Performance on older devices
  
  // Pregnancy-specific metrics
  imageOptimization: 90, // 90% images optimized
  accessibilityScore: 95, // High accessibility for all users
  performanceScore: 90 // Overall performance target
}

// URLs to monitor
const MONITORING_URLS = [
  'http://localhost:3000/', // Landing page
  'http://localhost:3000/family-feed', // Main feed
  'http://localhost:3000/feed/test-pregnancy' // Pregnancy-specific feed
]

class PregnancyPerformanceMonitor {
  constructor() {
    this.results = []
    this.violations = []
    this.chrome = null
  }

  async start() {
    console.log('🤱 Starting Preggo Performance Monitor...\n')
    
    try {
      // Launch Chrome
      this.chrome = await chromeLauncher.launch({
        chromeFlags: ['--headless', '--no-sandbox', '--disable-gpu']
      })

      // Monitor each URL
      for (const url of MONITORING_URLS) {
        console.log(`📊 Monitoring: ${url}`)
        await this.monitorURL(url)
      }

      // Generate report
      await this.generateReport()

      // Check for violations
      this.checkBudgetViolations()

      console.log('\n✅ Performance monitoring completed!')

    } catch (error) {
      console.error('❌ Performance monitoring failed:', error)
      process.exit(1)
    } finally {
      if (this.chrome) {
        await this.chrome.kill()
      }
    }
  }

  async monitorURL(url) {
    try {
      const options = {
        logLevel: 'info',
        output: 'json',
        onlyCategories: ['performance', 'accessibility'],
        onlyAudits: [
          'first-contentful-paint',
          'largest-contentful-paint',
          'cumulative-layout-shift',
          'interactive',
          'total-byte-weight',
          'unused-javascript',
          'unused-css-rules',
          'dom-size',
          'uses-webp-images',
          'uses-optimized-images',
          'accessibility'
        ],
        port: this.chrome.port
      }

      const runnerResult = await lighthouse(url, options)
      
      if (!runnerResult) {
        throw new Error('Lighthouse failed to run')
      }

      const metrics = this.extractMetrics(runnerResult.lhr, url)
      this.results.push(metrics)

      this.displayMetrics(metrics)

    } catch (error) {
      console.error(`❌ Failed to monitor ${url}:`, error.message)
    }
  }

  extractMetrics(lhr, url) {
    const audits = lhr.audits
    const categories = lhr.categories

    return {
      url,
      timestamp: new Date().toISOString(),
      scores: {
        performance: Math.round(categories.performance.score * 100),
        accessibility: Math.round(categories.accessibility.score * 100)
      },
      metrics: {
        firstContentfulPaint: audits['first-contentful-paint']?.numericValue || 0,
        largestContentfulPaint: audits['largest-contentful-paint']?.numericValue || 0,
        cumulativeLayoutShift: audits['cumulative-layout-shift']?.numericValue || 0,
        timeToInteractive: audits['interactive']?.numericValue || 0,
        totalTransferSize: audits['total-byte-weight']?.numericValue || 0,
        unusedJavaScript: audits['unused-javascript']?.details?.overallSavingsBytes || 0,
        unusedCSS: audits['unused-css-rules']?.details?.overallSavingsBytes || 0,
        domSize: audits['dom-size']?.numericValue || 0
      },
      optimizations: {
        usesWebP: audits['uses-webp-images']?.score === 1,
        usesOptimizedImages: audits['uses-optimized-images']?.score === 1
      }
    }
  }

  displayMetrics(metrics) {
    console.log(`\n📈 Performance Results for ${metrics.url}:`)
    console.log(`   Performance Score: ${metrics.scores.performance}% ${this.getScoreEmoji(metrics.scores.performance)}`)
    console.log(`   Accessibility Score: ${metrics.scores.accessibility}% ${this.getScoreEmoji(metrics.scores.accessibility)}`)
    console.log(`\n   Core Web Vitals:`)
    console.log(`   🎨 First Contentful Paint: ${Math.round(metrics.metrics.firstContentfulPaint)}ms ${this.getBudgetStatus('firstContentfulPaint', metrics.metrics.firstContentfulPaint)}`)
    console.log(`   🖼️  Largest Contentful Paint: ${Math.round(metrics.metrics.largestContentfulPaint)}ms ${this.getBudgetStatus('largestContentfulPaint', metrics.metrics.largestContentfulPaint)}`)
    console.log(`   📐 Cumulative Layout Shift: ${metrics.metrics.cumulativeLayoutShift.toFixed(3)} ${this.getBudgetStatus('cumulativeLayoutShift', metrics.metrics.cumulativeLayoutShift)}`)
    console.log(`   ⚡ Time to Interactive: ${Math.round(metrics.metrics.timeToInteractive)}ms ${this.getBudgetStatus('timeToInteractive', metrics.metrics.timeToInteractive)}`)
    
    console.log(`\n   Resource Usage:`)
    console.log(`   📦 Total Transfer Size: ${Math.round(metrics.metrics.totalTransferSize / 1024)}KB ${this.getBudgetStatus('totalTransferSize', metrics.metrics.totalTransferSize)}`)
    console.log(`   🗑️  Unused JavaScript: ${Math.round(metrics.metrics.unusedJavaScript / 1024)}KB ${this.getBudgetStatus('unusedJavaScript', metrics.metrics.unusedJavaScript)}`)
    console.log(`   🎨 Unused CSS: ${Math.round(metrics.metrics.unusedCSS / 1024)}KB ${this.getBudgetStatus('unusedCSS', metrics.metrics.unusedCSS)}`)
    console.log(`   🌳 DOM Size: ${metrics.metrics.domSize} nodes ${this.getBudgetStatus('domSize', metrics.metrics.domSize)}`)

    console.log(`\n   Image Optimizations:`)
    console.log(`   🖼️  WebP Images: ${metrics.optimizations.usesWebP ? '✅' : '❌'}`)
    console.log(`   🎯 Optimized Images: ${metrics.optimizations.usesOptimizedImages ? '✅' : '❌'}`)
  }

  getScoreEmoji(score) {
    if (score >= 90) return '🟢'
    if (score >= 70) return '🟡'
    return '🔴'
  }

  getBudgetStatus(metric, value) {
    const budget = PERFORMANCE_BUDGETS[metric]
    if (!budget) return ''
    
    const isWithinBudget = value <= budget
    
    if (!isWithinBudget) {
      this.violations.push({
        metric,
        value,
        budget,
        url: this.results[this.results.length - 1]?.url
      })
    }
    
    return isWithinBudget ? '✅' : '❌'
  }

  checkBudgetViolations() {
    if (this.violations.length === 0) {
      console.log('\n🎉 All performance budgets met!')
      return
    }

    console.log(`\n⚠️  Found ${this.violations.length} budget violations:`)
    
    this.violations.forEach(violation => {
      const percentage = ((violation.value - violation.budget) / violation.budget * 100).toFixed(1)
      console.log(`   ${violation.metric}: ${violation.value} (${percentage}% over budget of ${violation.budget})`)
      console.log(`   URL: ${violation.url}`)
    })

    // Pregnancy-specific advice
    console.log(`\n🤱 Pregnancy App Performance Tips:`)
    
    if (this.violations.some(v => v.metric.includes('Paint'))) {
      console.log('   • Optimize images for expecting mothers who may have slower connections')
      console.log('   • Consider pregnancy-themed loading placeholders to reduce anxiety')
    }
    
    if (this.violations.some(v => v.metric === 'cumulativeLayoutShift')) {
      console.log('   • Stable layouts are crucial for users experiencing pregnancy symptoms')
      console.log('   • Reserve space for dynamic content like baby size comparisons')
    }
    
    if (this.violations.some(v => v.metric.includes('unused'))) {
      console.log('   • Remove unused code to improve performance on battery-conscious devices')
      console.log('   • Consider lazy loading non-critical pregnancy features')
    }
  }

  async generateReport() {
    const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0]
    const reportPath = path.join(process.cwd(), `performance-report-${timestamp}.json`)
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalURLs: this.results.length,
        budgetViolations: this.violations.length,
        averagePerformanceScore: this.results.reduce((sum, r) => sum + r.scores.performance, 0) / this.results.length,
        averageAccessibilityScore: this.results.reduce((sum, r) => sum + r.scores.accessibility, 0) / this.results.length
      },
      budgets: PERFORMANCE_BUDGETS,
      results: this.results,
      violations: this.violations,
      pregnancySpecificNotes: [
        'Performance is critical for users experiencing pregnancy symptoms',
        'Fast loading reduces anxiety during vulnerable moments',
        'Stable layouts prevent discomfort from unexpected changes',
        'Optimized images are essential for sharing pregnancy milestones',
        'Accessibility ensures inclusive experience for all family members'
      ]
    }

    await fs.writeFile(reportPath, JSON.stringify(report, null, 2))
    console.log(`\n📊 Detailed report saved to: ${reportPath}`)
  }
}

// CLI execution
if (require.main === module) {
  const monitor = new PregnancyPerformanceMonitor()
  monitor.start().catch(error => {
    console.error('❌ Monitoring failed:', error)
    process.exit(1)
  })
}

module.exports = PregnancyPerformanceMonitor
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  
  // Store original console methods
  const originalConsole = {
    log: console.log,
    warn: console.warn,
    error: console.error,
    info: console.info,
    debug: console.debug
  }

  // Function to send logs to backend
  const sendLogToBackend = async (level: string, message: string, metadata?: string) => {
    try {
      await $fetch(`${config.public.apiBase}/logs/frontend`, {
        method: 'POST',
        body: {
          level,
          message,
          timestamp: new Date().toISOString(),
          metadata
        }
      })
    } catch (error) {
      // Fail silently to avoid infinite loops
    }
  }

  // Function to stringify arguments
  const stringifyArgs = (args: any[]) => {
    return args.map(arg => {
      if (typeof arg === 'object') {
        try {
          return JSON.stringify(arg, null, 2)
        } catch {
          return String(arg)
        }
      }
      return String(arg)
    }).join(' ')
  }

  // Patch console.log
  console.log = (...args: any[]) => {
    const message = stringifyArgs(args)
    originalConsole.log(...args)
    sendLogToBackend('info', message)
  }

  // Patch console.warn
  console.warn = (...args: any[]) => {
    const message = stringifyArgs(args)
    originalConsole.warn(...args)
    sendLogToBackend('warning', message)
  }

  // Patch console.error
  console.error = (...args: any[]) => {
    const message = stringifyArgs(args)
    originalConsole.error(...args)
    sendLogToBackend('error', message)
  }

  // Patch console.info
  console.info = (...args: any[]) => {
    const message = stringifyArgs(args)
    originalConsole.info(...args)
    sendLogToBackend('info', message)
  }

  // Patch console.debug
  console.debug = (...args: any[]) => {
    const message = stringifyArgs(args)
    originalConsole.debug(...args)
    sendLogToBackend('debug', message)
  }

  // Capture unhandled errors
  window.addEventListener('error', (event) => {
    const message = `${event.error?.message || event.message} at ${event.filename}:${event.lineno}:${event.colno}`
    sendLogToBackend('error', message, 'unhandled-error')
  })

  // Capture unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    const message = `Unhandled promise rejection: ${event.reason}`
    sendLogToBackend('error', message, 'unhandled-promise-rejection')
  })
})
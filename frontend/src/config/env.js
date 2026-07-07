/**
 * Centralized environment variable configuration for the frontend.
 * All import.meta.env reads should occur here with sensible default/fallback values.
 */
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  appName: import.meta.env.VITE_APP_NAME || "Council of Minds",
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  mode: import.meta.env.MODE,
};

export default env;

import axios from "axios";
import { env } from "../config/env";
import { handleApiError } from "../lib/apiErrorHandler";

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const store = window.__COM_AUTH_STORE__ || null;
    let token = null;
    if (store) {
      token = store.getState().accessToken;
    } else {
      try {
        const stored = localStorage.getItem("com_auth_storage");
        if (stored) {
          const parsed = JSON.parse(stored);
          token = parsed?.state?.accessToken;
        }
      } catch {
        // ignore storage parse errors
      }
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor to handle 401 and refresh token once
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {};

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        let refreshToken = null;
        const store = window.__COM_AUTH_STORE__ || null;
        if (store) {
          refreshToken = store.getState().refreshToken;
        } else {
          try {
            const stored = localStorage.getItem("com_auth_storage");
            if (stored) {
              const parsed = JSON.parse(stored);
              refreshToken = parsed?.state?.refreshToken;
            }
          } catch {
            // ignore
          }
        }

        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        const res = await axios.post(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newAccessToken = res.data.access_token;
        const newRefreshToken = res.data.refresh_token;

        if (store) {
          store.getState().setTokens(newAccessToken, newRefreshToken);
        } else {
          try {
            const stored = localStorage.getItem("com_auth_storage");
            const parsed = stored ? JSON.parse(stored) : { state: {} };
            parsed.state.accessToken = newAccessToken;
            parsed.state.refreshToken = newRefreshToken;
            parsed.state.isAuthenticated = true;
            localStorage.setItem("com_auth_storage", JSON.stringify(parsed));
          } catch {
            // ignore
          }
        }

        apiClient.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        processQueue(null, newAccessToken);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        const store = window.__COM_AUTH_STORE__ || null;
        if (store) {
          store.getState().logout();
        } else {
          localStorage.removeItem("com_auth_storage");
        }
        if (window.location.pathname !== "/login") {
          handleApiError(refreshError, "Session Expired");
          window.location.href = "/login?expired=true";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (!originalRequest._skipGlobalError) {
      handleApiError(error);
    }
    return Promise.reject(error);
  },
);

export default apiClient;

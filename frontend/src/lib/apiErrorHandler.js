import useUiStore from "../store/uiStore";

/**
 * Maps HTTP error responses or network errors to consistent Toast notifications.
 */
export const handleApiError = (error, customTitle = null) => {
  const store = window.__COM_UI_STORE__ || useUiStore;
  const addToast = store.getState().addToast;

  if (!error.response) {
    // Network error or request aborted
    addToast({
      title: customTitle || "Network Error",
      message:
        error.message ||
        "Unable to connect to the server. Please check your network connection.",
      type: "error",
      duration: 5000,
    });
    return;
  }

  const status = error.response.status;
  const data = error.response.data;

  let title = customTitle || `Error (${status})`;
  let message = "An unexpected error occurred. Please try again.";

  if (data && data.detail) {
    if (typeof data.detail === "string") {
      message = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      // FastAPI validation error array
      const firstErr = data.detail[0];
      const field = firstErr.loc ? firstErr.loc[firstErr.loc.length - 1] : "";
      message = field ? `${field}: ${firstErr.msg}` : firstErr.msg;
    }
  } else if (data && data.message) {
    message = data.message;
  }

  switch (status) {
    case 400:
      title = customTitle || "Bad Request";
      break;
    case 401:
      title = customTitle || "Authentication Failed";
      if (
        !message ||
        message === "An unexpected error occurred. Please try again."
      ) {
        message =
          "Your session has expired or is invalid. Please log in again.";
      }
      break;
    case 403:
      title = customTitle || "Access Denied";
      if (
        !message ||
        message === "An unexpected error occurred. Please try again."
      ) {
        message = "You do not have permission to perform this action.";
      }
      break;
    case 404:
      title = customTitle || "Not Found";
      if (
        !message ||
        message === "An unexpected error occurred. Please try again."
      ) {
        message = "The requested resource could not be found.";
      }
      break;
    case 413:
      title = customTitle || "File Too Large";
      message = "The uploaded file exceeds the maximum allowed size.";
      break;
    case 422:
      title = customTitle || "Validation Error";
      break;
    case 500:
    case 502:
    case 503:
    case 504:
      title = customTitle || "Server Error";
      if (
        !message ||
        message === "An unexpected error occurred. Please try again."
      ) {
        message =
          "A server error occurred on Council of Minds backend. Please try again later.";
      }
      break;
    default:
      break;
  }

  addToast({
    title,
    message,
    type: "error",
    duration: 5000,
  });
};

export default handleApiError;

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize global rate limiter using client remote IP address.
# In testing environment, disable rate limiting by default to prevent throttling test helper calls.
is_testing = os.environ.get("BACKEND_ENVIRONMENT", "").lower() in ["test", "testing"]
limiter = Limiter(key_func=get_remote_address, enabled=not is_testing)

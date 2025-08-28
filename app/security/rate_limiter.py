from slowapi import Limiter
from slowapi.util import get_remote_address

# Set up limiter with IP-based keys
limiter = Limiter(key_func=get_remote_address)
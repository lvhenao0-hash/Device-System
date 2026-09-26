from slowapi import Limiter
from slowapi.util import get_remote_address

# Instancia unica compartida por toda la app (se registra en app.state.limiter
# desde main.py). Las rutas la importan para usar el decorador @limiter.limit(...).
limiter = Limiter(key_func=get_remote_address)

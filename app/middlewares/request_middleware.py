"""Middleware personalizado exigido por EV11 (Fase 10):
mide el tiempo de respuesta, agrega X-Process-Time, X-App-Name y
X-Request-ID, y registra metodo/ruta/estado de cada peticion.
"""

import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger("device_systems")


async def request_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "%s %s -> %s | request_id=%s | time=%.4fs",
        request.method,
        request.url.path,
        response.status_code,
        request_id,
        process_time,
    )

    return response

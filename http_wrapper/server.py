from http_wrapper.routes.analysis import router as analysis_router
from http_wrapper.routes.notebook import router as notebook_router, on_exit
from http_wrapper.routes.git import router as git_router
from http_wrapper.jugex_logger import access_logger
from http_wrapper.conf.siibra_jugex_conf import SIIBRA_TOOLBOX_VIEWER_PLUGIN_STATIC_DIR

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Allow CORS
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['GET', 'POST'],
)

@app.get('/', include_in_schema=False)
def hello():
    return 'world'
    
@app.get('/ready', include_in_schema=False)
def hello():
    return 'OK'

@app.middleware('http')
async def access_log(request: Request, call_next):
    start_time = time.time()
    resp = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    access_logger.info(f'{request.method.upper()} {str(request.url)}', extra={
        'status': str(resp.status_code),
        'process_time_ms': str(round(process_time))
    })
    return resp

app.include_router(analysis_router, prefix="/analysis")
app.include_router(notebook_router, prefix="/notebook")
app.include_router(git_router, prefix="/git")

if SIIBRA_TOOLBOX_VIEWER_PLUGIN_STATIC_DIR:
    path_to_viewer_plugin = SIIBRA_TOOLBOX_VIEWER_PLUGIN_STATIC_DIR
    app.mount('/viewer_plugin', StaticFiles(directory=path_to_viewer_plugin))

from threading import Event

@app.on_event("shutdown")
def shutdown_event():
    # TODO doesn't work quite right
    # shutdown handler isn't called until ctrl+c is hit twice
    on_exit()


do_not_logs = (
    "GET / HTTP",
)

import logging
class EndpointLoggingFilter(logging.Filter):
    """Custom logger filter. Do not log metrics, ready endpoint."""
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return all(
            message.find(do_not_log) == -1 for do_not_log in do_not_logs
        )

logging.getLogger("uvicorn.access").addFilter(EndpointLoggingFilter())

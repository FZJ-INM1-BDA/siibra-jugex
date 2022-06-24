from http_wrapper.routes.analysis import router as analysis_router
from http_wrapper.routes.notebook import router as notebook_router
from http_wrapper.jugex_logger import access_logger

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from os import getenv
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

if getenv("SIIBRA_TOOLBOX_VIEWER_PLUGIN_STATIC_DIR"):
    path_to_viewer_plugin = getenv("SIIBRA_TOOLBOX_VIEWER_PLUGIN_STATIC_DIR")
    app.mount('/viewer_plugin', StaticFiles(directory=path_to_viewer_plugin))


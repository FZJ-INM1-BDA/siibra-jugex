from routes.analysis import router as analysis_router
from jugex_logger import access_logger

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from os import path, getenv
import time

path_to_static = path.join(
    path.dirname(__file__),
    "../siibra_jugex_viewerplugin",
    "public/"
)

if getenv("SIIBRA_JUGEX_STATIC_DIR"):
    path_to_static = getenv("SIIBRA_JUGEX_STATIC_DIR")

app = FastAPI()

# Allow CORS
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['GET', 'POST'],
)

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

@app.get('/', include_in_schema=False)
def hello():
    return 'world'

app.include_router(analysis_router, prefix="/analysis")
app.mount('/viewer_plugin', StaticFiles(directory=path_to_static))


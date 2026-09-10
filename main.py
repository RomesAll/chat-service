from bootstrap import set_bootstrap
from app.shared.config import config
set_bootstrap(config)
from starlette.middleware.cors import CORSMiddleware
from app.presentation.rest_api import register_route
from fastapi import FastAPI
import uvicorn
import app.shared.log_config.log_config


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_route(app)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
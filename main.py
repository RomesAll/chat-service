from bootstrap import set_bootstrap
from app.shared.config import DevelopConfig

config = DevelopConfig()
set_bootstrap(config)

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.presentation.rest_api.websocket.websocket import route as ws_route
from app.presentation.rest_api.messages.messages import route as msg_route
from app.presentation.rest_api.users.get_users import route as get_users_route
from app.presentation.rest_api.room.room import route as save_user_in_room_route
from app.presentation.rest_api.users.update_users import route as update_users_route
from app.presentation.rest_api.users.delete_users import route as delete_users_route
from app.presentation.rest_api.keys.keys import route as keys_route
from app.presentation.rest_api.auth.auth import route as auth_route
from app.presentation.rest_api.db.database import route as db_route
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ws_route)
app.include_router(msg_route, prefix='/api/v1')
app.include_router(get_users_route, prefix='/api/v1')
app.include_router(update_users_route, prefix='/api/v1')
app.include_router(delete_users_route, prefix='/api/v1')
app.include_router(auth_route, prefix='/api/v1')
app.include_router(keys_route, prefix='/api/v1')
app.include_router(save_user_in_room_route, prefix='/api/v1')
app.include_router(db_route, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)

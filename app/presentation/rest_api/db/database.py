from fastapi import APIRouter
from bootstrap import get_bootstrap
from app.business_logic.unit_of_work import UnitOfWork
from app.data_access.database.models.base import BaseOrm

route = APIRouter()

@route.post(path='/drop-db', tags=['Database'])
def drop_db():
    with UnitOfWork(get_bootstrap().database) as uow:
        BaseOrm.metadata.drop_all(get_bootstrap().database.engine)


@route.post(path='/create-db', tags=['Database'])
def create_db():
    with UnitOfWork(get_bootstrap().database) as uow:
        BaseOrm.metadata.create_all(get_bootstrap().database.engine)
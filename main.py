from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.shared.dtos.base import BaseDtoCreateUpdateDeleteWithReturnValueRequest, BaseDtoGetListRequest, \
    PaginationDto, SortDto, SortEnum, FilterDto, OperatorEnum
from app.shared.dtos.room import RoomDtoGetResponse
from models.metaclasses import AutoCreateTable
# from app.business_logic.dtos.base import (
#     DtoGetByIdRequest,
#     BaseDtoGetRequest,
#     BaseDtoPostRequest,
#     BaseDtoUpdateRequest,
#     BaseDtoDeleteRequest,
#     BaseDtoGetResponse,
# )
from repositories.base import BaseRepository

engine = create_engine(url='sqlite:///test.db')
session_factory = sessionmaker(bind=engine)
AutoCreateTable.set_engine(engine)

from models.room import RoomOrm

with session_factory() as session:
    repository = BaseRepository(
        dto_response=RoomDtoGetResponse,
        session=session,
        model=RoomOrm
    )
    dto_request: BaseDtoGetListRequest = BaseDtoGetListRequest(
        pagination=PaginationDto(limit=1, offset=0),
        include_deleted=True,
        sort=[SortDto(field='name', order_mode=SortEnum.DESC), SortDto(field='id', order_mode=SortEnum.DESC)],
        filters=[FilterDto(field='name', operator=OperatorEnum.EQ, value='aboba'), FilterDto(field='name', operator=OperatorEnum.EQ, value='bab')],
        filters_logic='OR'
    )
    result = repository.get(dto_request)
    session.commit()

print(result)
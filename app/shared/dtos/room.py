from base import (
    BaseDtoOrmRecordGetResponse,
    BaseDtoOrmRecordPostRequest,
    BaseDtoOrmRecordPutResponse,
    BaseDtoOrmRecordDeleteResponse
)


class RoomDtoGetResponse(BaseDtoOrmRecordGetResponse):
    """Room DTO для операции получения (Get) информации о комнате"""
    name: str


class RoomDtoPostRequest(RoomDtoGetResponse, BaseDtoOrmRecordPostRequest):
    """Room DTO для операции добавления (Post) информации о комнате"""
    pass


class RoomDtoUpdateRequest(BaseDtoOrmRecordPutResponse):
    """Room DTO для операции обновления (Put) информации о комнате"""
    name: str


class RoomDtoDeleteRequest(BaseDtoOrmRecordDeleteResponse):
    """Room DTO для операции удаления (Delete) информации о комнате"""
    pass
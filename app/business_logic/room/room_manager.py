from repositories.room import RoomRepository
from shared.dtos.base import DtoIdRecordRequest, BaseDtoGetListRequest
from shared.dtos.room import RoomDtoPostRequest, RoomDtoGetResponse, RoomDtoUpdateRequest, RoomDtoDeleteRequest


class RoomManager:
    def __init__(self, room_repo: RoomRepository):
        self.room_repo = room_repo

    def get(
            self,
            dto_get_request: BaseDtoGetListRequest
    ):
        """
        Получение списка комнат
        :param dto_get_request:
        :return:
        """
        users: list[RoomDtoGetResponse] = self.room_repo.get(dto_get_request)
        return users

    def get_one(
            self,
            dto_record_id: DtoIdRecordRequest
    ) -> RoomDtoGetResponse:
        """
        Получение пользователя по id
        :param dto_record_id: принимает DtoIdRecordRequest с id типа (int, UUID, str)
        :return: отдает объект RoomDtoGetResponse (дочерний объект BaseDtoGetResponse)
        """
        user: RoomDtoGetResponse = self.room_repo.get_by_id(dto_record_id)
        return user

    def save(
            self,
            dto_post_request: RoomDtoPostRequest
    ):
        """
        Сохранение пользователей
        :param dto_post_request:
        :return:
        """
        result: RoomDtoGetResponse | None = self.room_repo.save(dto_post_request)
        return result

    def update(
            self,
            dto_update_request: RoomDtoUpdateRequest
    ):
        """
        Обновление данных пользователей
        :param dto_update_request:
        :return:
        """
        result: RoomDtoGetResponse | None = self.room_repo.update(dto_update_request)
        return result

    def soft_delete(
            self,
            dto_delete_request: RoomDtoDeleteRequest
    ) -> RoomDtoGetResponse | bool | None:
        """
        Мягкое удаление пользователя с возможностью восстановления
        :param dto_delete_request:
        :return:
        """
        result: RoomDtoGetResponse | bool | None = self.room_repo.soft_delete(dto_delete_request)
        return result

    def hard_delete(
            self,
            dto_delete_request: RoomDtoDeleteRequest
    ) -> RoomDtoGetResponse | bool | None:
        """
        Жесткое удаление пользователя без возможности восстановления
        :param dto_delete_request:
        :return:
        """
        result: RoomDtoGetResponse | bool | None = self.room_repo.hard_delete(dto_delete_request)
        return result

    def recovery(
            self,
            dto_delete_request: RoomDtoDeleteRequest
    ) -> RoomDtoGetResponse | bool | None:
        """
        Восстановление пользователя
        :param dto_delete_request:
        :return:
        """
        result: RoomDtoGetResponse | bool | None = self.room_repo.recovery(dto_delete_request)
        return result
from repositories.user import UserRepository
from shared.dtos.base import DtoIdRecordRequest, BaseDtoGetListRequest
from shared.dtos.user import UserDtoGetResponse, UserDtoPostRequest, UserDtoUpdateRequest, UserDtoDeleteRequest


class UserManager:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get(
            self,
            dto_get_request: BaseDtoGetListRequest
    ):
        """
        Получение списка пользователей
        :param dto_get_request:
        :return:
        """
        users: list[UserDtoGetResponse] = self.user_repo.get(dto_get_request)
        return users

    def get_one(
            self,
            dto_record_id: DtoIdRecordRequest
    ) -> UserDtoGetResponse:
        """
        Получение пользователя по id
        :param dto_record_id: принимает DtoIdRecordRequest с id типа (int, UUID, str)
        :return: отдает объект UserDtoGetResponse (дочерний объект BaseDtoGetResponse)
        """
        user: UserDtoGetResponse = self.user_repo.get_by_id(dto_record_id)
        return user

    def save(
            self,
            dto_post_request: UserDtoPostRequest
    ):
        """
        Сохранение пользователей
        :param dto_post_request:
        :return:
        """
        result: UserDtoGetResponse | None = self.user_repo.save(dto_post_request)
        return result

    def update(
            self,
            dto_update_request: UserDtoUpdateRequest
    ):
        """
        Обновление данных пользователей
        :param dto_update_request:
        :return:
        """
        result: UserDtoGetResponse | None = self.user_repo.update(dto_update_request)
        return result

    def soft_delete(
            self,
            dto_delete_request: UserDtoDeleteRequest
    ) -> UserDtoGetResponse | bool | None:
        """
        Мягкое удаление пользователя с возможностью восстановления
        :param dto_delete_request:
        :return:
        """
        result: UserDtoGetResponse | bool | None = self.user_repo.soft_delete(dto_delete_request)
        return result

    def hard_delete(
            self,
            dto_delete_request: UserDtoDeleteRequest
    ) -> UserDtoGetResponse | bool | None:
        """
        Жесткое удаление пользователя без возможности восстановления
        :param dto_delete_request:
        :return:
        """
        result: UserDtoGetResponse | bool | None = self.user_repo.hard_delete(dto_delete_request)
        return result

    def recovery(
            self,
            dto_delete_request: UserDtoDeleteRequest
    ) -> UserDtoGetResponse | bool | None:
        """
        Восстановление пользователя
        :param dto_delete_request:
        :return:
        """
        result: UserDtoGetResponse | bool | None = self.user_repo.recovery(dto_delete_request)
        return result
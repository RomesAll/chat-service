from app.business_logic.unit_of_work import UnitOfWork
from app.business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import UserInRoomPostRequest, UserInRoomResponse
from app.data_access.database.repositories import UserRepository
from app.data_access.database.repositories.room import UserInRoomRepository, RoomRepository


class SaveUserInRoomUseCase(IUseCase):
    """Use case для добавления пользователя в комнату"""
    def __init__(
            self,
            uow: UnitOfWork,
    ):
        self.uow = uow

    def execute(self, dto_request: UserInRoomPostRequest) -> UserInRoomResponse:
        with self.uow as uow:
            room_repo = uow.get_repository(RoomRepository)
            user_in_room_repo = uow.get_repository(UserInRoomRepository)
            user_repo = uow.get_repository(UserRepository)
            if not room_repo.check_exist(dto_request.room_id):
                raise Exception
            if not user_repo.check_exist(dto_request.user_id):
                raise Exception
            result = user_in_room_repo.save(dto_request)
            return result
from business_logic.active_session.active_session_manager import active_session_manager
from business_logic.use_cases.interface.iuse_case import IUseCase
from app.shared.dtos import ActionType, BaseDtoClientRequest, BaseDtoGetListRequest, InvitationUserInRoomDtoRequest


class UseCaseRegistry:
    """Реестр связи ActionType -> UseCase"""
    _registry: dict[ActionType, type[IUseCase]] = {}

    @classmethod
    def register_use_case(
            cls,
            action_type: ActionType,
            use_case_class: type[IUseCase]
    ):
        cls._registry[action_type] = use_case_class

    @classmethod
    def get(
            cls,
            dto_request: BaseDtoClientRequest | BaseDtoGetListRequest | InvitationUserInRoomDtoRequest,
            action_type: ActionType
    ):
        try:
            use_case_class = cls._registry[action_type]
            return use_case_class(dto_request, action_type, active_session_manager)
        except KeyError:
            raise Exception
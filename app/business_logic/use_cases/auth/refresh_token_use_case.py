from uuid import uuid4
from business_logic.auth.jwt_manager import JWTFacade
from business_logic.cache.jwt_white_list import JWTWhiteListCache
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos import JWTRefreshTokenResponse
from dtos.jwt import JWTTokenResponse


class RefreshTokenUseCase(IUseCase):
    """Use case для обновления токенов"""
    def __init__(
            self,
            jwt_facade: type[JWTFacade],
            jwt_white_list: JWTWhiteListCache
    ):
        self.jwt_facade = jwt_facade
        self.jwt_white_list = jwt_white_list

    def execute(self, refresh_token: JWTRefreshTokenResponse) -> JWTTokenResponse:
        new_refresh_id = uuid4()
        self.jwt_white_list.update_refresh(
            user_id=refresh_token.user_id,
            old_refresh_id=refresh_token.refresh_id,
            new_refresh_id=new_refresh_id
        )
        return self.jwt_facade.create_tokens(
            user_id=refresh_token.user_id,
            role=refresh_token.role,
            sub=refresh_token.sub,
            refresh_id=new_refresh_id
        )
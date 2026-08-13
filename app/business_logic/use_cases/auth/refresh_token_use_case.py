from uuid import uuid4
from business_logic.auth.jwt_manager import JWTFacade
from business_logic.cache.jwt_white_list import JWTWhiteListCache
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos import JWTRefreshToken
from dtos.jwt import JWTRefreshTokenResponse


class RefreshTokenUseCase(IUseCase):
    """Use case для обновления токенов"""
    def __init__(
            self,
            jwt_manager: type[JWTFacade],
            jwt_white_list: JWTWhiteListCache
    ):
        self.jwt_manager = jwt_manager
        self.jwt_white_list = jwt_white_list

    def execute(self, refresh_token: str) -> JWTRefreshTokenResponse:
        token: JWTRefreshToken = self.jwt_manager.jwt_refresh_manager.decode_token(
            refresh_token
        )
        new_refresh_id = uuid4()
        self.jwt_white_list.update_refresh(
            user_id=token.user_id,
            old_refresh_id=token.refresh_id,
            new_refresh_id=new_refresh_id
        )
        return self.jwt_manager.create_tokens(
            user_id=token.user_id,
            role=token.role,
            sub=token.sub,
            refresh_id=new_refresh_id
        )
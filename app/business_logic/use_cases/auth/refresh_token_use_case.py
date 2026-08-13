from business_logic.auth.jwt_manager import JWTFacade
from business_logic.auth.password_manager import PasswordManager
from business_logic.use_cases.interface.iuse_case import IUseCase
from dtos import JWTRefreshToken
from dtos.jwt import JWTRefreshTokenResponse


class RefreshTokenUseCase(IUseCase):

    def __init__(
            self,
            jwt_manager: type[JWTFacade]
    ):
        self.jwt_manager = jwt_manager

    def execute(self, refresh_token: str) -> JWTRefreshTokenResponse:
        token: JWTRefreshToken = self.jwt_manager.jwt_refresh_manager.decode_token(
            refresh_token
        )
        return self.jwt_manager.create_tokens(token.user_id, token.sub)
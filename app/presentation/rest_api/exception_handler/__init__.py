from fastapi import FastAPI
from app.business_logic.exceptions import CheckPswError, RefreshTokenInActive, VerifyCodeStorageError, \
    VerifyCodeInCorrect, CheckMasterPswError
from app.data_access.exceptions import RecordNotFound, UniqueViolationError, NotNullViolationError
from app.presentation.rest_api.exception_handler.auth_exc_handler import psw_error_master_key, psw_error, refresh_token_in_active
from app.presentation.rest_api.exception_handler.room_exc_handler import room_not_found, room_is_exists, room_missing_info
from app.presentation.rest_api.exception_handler.user_exc_handler import user_not_found, user_is_exists, user_missing_info, user_verify_code_error, user_verify_code_incorrect

def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(CheckMasterPswError, psw_error_master_key)
    app.add_exception_handler(CheckPswError, psw_error)
    app.add_exception_handler(RefreshTokenInActive, refresh_token_in_active)

    app.add_exception_handler(RecordNotFound, room_not_found)
    app.add_exception_handler(UniqueViolationError, room_is_exists)
    app.add_exception_handler(NotNullViolationError, room_missing_info)

    app.add_exception_handler(RecordNotFound, user_not_found)
    app.add_exception_handler(UniqueViolationError, user_is_exists)
    app.add_exception_handler(NotNullViolationError, user_missing_info)
    app.add_exception_handler(VerifyCodeStorageError, user_verify_code_error)
    app.add_exception_handler(VerifyCodeInCorrect, user_verify_code_incorrect)

__version__ = 'v1.3.1'
__author__ = 'RomesAll'
__all__ = [
    'register_exception_handler'
]